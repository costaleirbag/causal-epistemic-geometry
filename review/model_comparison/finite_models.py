"""Finite rank-one logistic models; NumPy only. No private data access."""
import time
import numpy as np


def contrasts(n):
    q = np.zeros((n, n-1))
    for j in range(n-1):
        q[:j+1, j] = 1 / np.sqrt((j+1)*(j+2))
        q[j+1, j] = -(j+1) / np.sqrt((j+1)*(j+2))
    return q


def sigmoid(z):
    return np.exp(-np.logaddexp(0., -z))


class Model:
    def __init__(self, name, x, families, penalty):
        self.name, self.x, self.f, self.lam = name, np.asarray(x), families, penalty
        self.k, self.d = self.x.shape
        self.fi, self.ki = contrasts(families), contrasts(self.k)
        dims = [('a', families)]
        if name in 'R D I C'.split(): dims += [('b', self.k-1)]
        if name == 'D': dims += [('h', families-1)]
        if name in ['G', 'H']: dims += [('beta', self.d)]
        if name in ['I', 'C', 'H']:
            dims += [('u', families-1), ('q', self.k-1 if name == 'I' else self.d)]
        self.slices, offset = {}, 0
        for key, size in dims:
            self.slices[key] = slice(offset, offset+size)
            offset += size
        self.size = offset

    def unpack(self, t):
        return {key: t[sl] for key, sl in self.slices.items()}

    def initial(self, start):
        rng = np.random.Generator(np.random.PCG64(20260910+start))
        t = np.zeros(self.size)
        for key in (['b'] if self.name == 'D' else ['u', 'q']):
            if key in self.slices:
                sl = self.slices[key]
                t[sl] = rng.normal(size=sl.stop-sl.start)*.1
                if key == 'q': t[sl] /= np.linalg.norm(t[sl])
        return t

    def logits(self, t, x=None):
        z = self.unpack(t)
        xx = self.x if x is None else x
        eta = np.broadcast_to(z['a'][:, None], (self.f, len(xx))).copy()
        if 'b' in z:
            b = self.ki @ z['b']
            d = np.exp(self.fi @ z['h']) if 'h' in z else np.ones(self.f)
            eta += d[:, None]*b
        if 'beta' in z: eta += xx @ z['beta']
        if 'u' in z:
            right = z['q']/np.linalg.norm(z['q'])
            v = self.ki @ right if self.name == 'I' else xx @ right
            eta += (self.fi @ z['u'])[:, None]*v
        return eta

    def objective(self, t, y, n):
        z = self.unpack(t)
        eta = self.logits(t)
        residual = n*sigmoid(eta)-y
        loss = np.sum(n*np.logaddexp(0., eta)-y*eta)
        grads = {'a': residual.sum(1)}
        if 'b' in z:
            b = self.ki @ z['b']
            d = np.exp(self.fi @ z['h']) if 'h' in z else np.ones(self.f)
            grads['b'] = self.ki.T @ (residual*d[:, None]).sum(0)
            if 'h' in z: grads['h'] = self.fi.T @ (d*(residual @ b))
        if 'beta' in z: grads['beta'] = self.x.T @ residual.sum(0)
        if 'u' in z:
            radius = np.linalg.norm(z['q'])
            right = z['q']/radius
            design = self.ki if self.name == 'I' else self.x
            u = self.fi @ z['u']
            grads['u'] = self.fi.T @ (residual @ (design @ right))
            g = design.T @ (residual.T @ u)
            grads['q'] = (g-right*(right @ g))/radius
        out = np.zeros_like(t)
        for key, val in z.items():
            weight = .01 if key == 'a' else (0 if key == 'q' else self.lam)
            loss += .5*weight*(val @ val)
            out[self.slices[key]] = grads[key]+weight*val
        return float(loss), out

    def gradient_norm(self, t, g):
        g = g.copy()
        if 'q' in self.slices:
            sl = self.slices['q']
            g[sl] *= max(1., np.linalg.norm(t[sl]))
        return float(np.max(np.abs(g)))


def fit(model, y, n, start=0, gate=lambda: None):
    cpu, wall = time.process_time(), time.monotonic()
    t = model.initial(start)
    inverse = np.eye(len(t))
    total = float(np.broadcast_to(n, y.shape).sum())
    status = 'iteration_limit'
    evaluations = 0
    def evaluate(t):
        nonlocal evaluations
        gate(); evaluations += 1
        with np.errstate(over='ignore', invalid='ignore', divide='ignore'):
            return model.objective(t, y, n)
    value, grad = evaluate(t)
    for iteration in range(3001):
        norm = model.gradient_norm(t, grad)/total
        if not np.isfinite(value) or not np.isfinite(grad).all():
            status = 'nonfinite'; break
        if norm <= 1e-9:
            status = 'converged'; break
        if iteration == 3000: break
        direction = -inverse @ grad
        if grad @ direction >= 0:
            inverse = np.eye(len(t)); direction = -grad
        step = 1.
        for _ in range(40):
            candidate = t+step*direction
            nv, ng = evaluate(candidate)
            if np.isfinite(nv) and np.isfinite(ng).all() and nv <= value+1e-4*step*(grad @ direction): break
            step *= .5
        else:
            status = 'line_search_failed'; break
        s, v = candidate-t, ng-grad
        sy = s @ v
        if sy > 1e-12*np.linalg.norm(s)*np.linalg.norm(v):
            hv = inverse @ v
            inverse += ((sy+v @ hv)/(sy*sy))*np.outer(s,s) - (np.outer(hv,s)+np.outer(s,hv))/sy
        else: inverse = np.eye(len(t))
        t, value, grad = candidate, nv, ng
    if 'q' in model.slices:
        sl = model.slices['q']
        right = t[sl]/np.linalg.norm(t[sl])
        physical = model.ki @ right if model.name == 'I' else right
        first = np.flatnonzero(np.abs(physical) > 1e-14)
        if len(first) and physical[first[0]] < 0:
            t[sl] *= -1; t[model.slices['u']] *= -1
    return dict(parameters=t.tolist(), status=status, iterations=iteration,
                objective=value, gradient_per_trial=norm, evaluations=evaluations,
                cpu_seconds=time.process_time()-cpu, wall_seconds=time.monotonic()-wall)


def split_panel(y, x, stage, split):
    if stage == 'A':
        train = np.arange(4)+4*split
        test = np.arange(4)+4*(1-split)
        centered = x-x.mean(0)
        return y[:, :, train].sum(2), np.full(y.shape[:2], 4.), y[:, :, test], centered, centered
    train = np.array([k for k in range(y.shape[1]) if k != split])
    center = x[train].mean(0)
    return y[:, train].sum(2), np.full((y.shape[0], len(train)), 8.), y[:, split:split+1], x[train]-center, x[split:split+1]-center


def losses(eta, y):
    raw = sigmoid(eta)
    p = np.clip(raw, 1e-6, 1-1e-6)
    ll = -(y*np.log(p[:, :, None])+(1-y)*np.log1p(-p[:, :, None]))
    br = (y-p[:, :, None])**2
    return dict(log_loss=float(ll.mean()), brier=float(br.mean()),
                family_log_loss=ll.mean((1,2)).tolist(), family_brier=br.mean((1,2)).tolist(),
                controller_log_loss=ll.mean((0,2)).tolist(), controller_brier=br.mean((0,2)).tolist(),
                clipped_cells=int(np.count_nonzero(raw != p)))
