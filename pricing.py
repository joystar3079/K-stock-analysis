"""가격 모형 — 전량 벡터화된 미국식 이항 트리와 IV 역산.

기존 구현은 옵션 1건마다 이분법 50회 x 트리 50스텝 = 2,500회의 작은 NumPy
호출을 발생시켰습니다. 옵션 3,000건이면 750만 회이고, 이 규모에서는 연산
자체보다 NumPy 호출 오버헤드가 지배합니다. ThreadPoolExecutor는 순수 CPU
연산에 GIL이 걸려 사실상 직렬 실행되므로 도움이 되지 않았습니다.

여기서는 모든 옵션을 (n, N+1) 배열로 쌓아 이분법을 동시에 돌립니다.
호출 횟수가 750만 회에서 약 1,600회(= 32 x 50)로 줄어듭니다.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import norm

from config import TH


def binomial_batch(S, K, T, r, q, sigma, is_call, n_steps: int = TH.TREE_STEPS):
    """미국식 이항 트리를 전 종목 동시 평가. 모든 인자는 (n,) 배열."""
    S = np.asarray(S, dtype=float)
    K = np.asarray(K, dtype=float)
    T = np.asarray(T, dtype=float)
    sigma = np.asarray(sigma, dtype=float)
    is_call = np.asarray(is_call, dtype=bool)

    dt = T / n_steps
    u = np.exp(sigma * np.sqrt(dt))
    d = 1.0 / u
    p = (np.exp((r - q) * dt) - d) / (u - d)
    disc = np.exp(-r * dt)

    col = np.arange(n_steps + 1)
    # 만기 시점 기초자산 격자: S * d^(N-j) * u^j
    ST = S[:, None] * d[:, None] ** (n_steps - col) * u[:, None] ** col

    sign = np.where(is_call, 1.0, -1.0)[:, None]
    V = np.maximum(sign * (ST - K[:, None]), 0.0)

    dcol, pcol, disccol = d[:, None], p[:, None], disc[:, None]
    for _ in range(n_steps - 1, -1, -1):
        ST = ST[:, :-1] / dcol
        V = disccol * (pcol * V[:, 1:] + (1.0 - pcol) * V[:, :-1])
        V = np.maximum(V, sign * (ST - K[:, None]))
    return V[:, 0]


def solve_iv_batch(target, S, K, T, r, q, is_call,
                   n_steps: int = TH.TREE_STEPS,
                   max_iter: int = TH.BISECTION_ITER):
    """전 종목 동시 이분법. 반환 shape (n,), 무효 입력은 NaN."""
    target = np.asarray(target, dtype=float)
    valid = (
        np.isfinite(target) & (target > 0)
        & np.isfinite(S) & np.isfinite(K) & np.isfinite(T) & (T > 0)
    )
    out = np.full(target.shape, np.nan)
    if not valid.any():
        return out

    t, s, k, tau = target[valid], np.asarray(S)[valid], np.asarray(K)[valid], np.asarray(T)[valid]
    cp = np.asarray(is_call)[valid]

    lo = np.full(t.shape, TH.VOL_LO)
    hi = np.full(t.shape, TH.VOL_HI)
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        px = binomial_batch(s, k, tau, r, q, mid, cp, n_steps)
        too_high = px > t
        hi = np.where(too_high, mid, hi)
        lo = np.where(too_high, lo, mid)

    out[valid] = 0.5 * (lo + hi)
    return out


def bs_delta_batch(S, K, T, r, q, sigma, is_call):
    """블랙-숄즈 델타. 배당 연속수익률 보정 포함."""
    S = np.asarray(S, dtype=float)
    K = np.asarray(K, dtype=float)
    T = np.asarray(T, dtype=float)
    sigma = np.asarray(sigma, dtype=float)
    is_call = np.asarray(is_call, dtype=bool)

    out = np.full(S.shape, np.nan)
    ok = np.isfinite(sigma) & (sigma > 0) & np.isfinite(T) & (T > 0) & (S > 0) & (K > 0)
    if not ok.any():
        return out

    d1 = ((np.log(S[ok] / K[ok]) + (r - q + 0.5 * sigma[ok] ** 2) * T[ok])
          / (sigma[ok] * np.sqrt(T[ok])))
    disc_q = np.exp(-q * T[ok])
    out[ok] = np.where(is_call[ok], disc_q * norm.cdf(d1),
                       disc_q * (norm.cdf(d1) - 1.0))
    return out
