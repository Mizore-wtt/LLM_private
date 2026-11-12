"""Small NumPy references for the formulas in ATTACK_METHODS_zh.md.

These are new educational implementations, not the original authors' code.
No models, datasets, remote services, or GPU dependencies are loaded.

Run: python 4_Attack/attack_baselines_numpy.py --self-check
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence
import argparse

import numpy as np


def _matrix(value: np.ndarray) -> np.ndarray:
    a = np.asarray(value)
    if a.ndim != 2 or not a.shape[1]:
        raise ValueError('Expected a two-dimensional matrix with nonempty features.')
    if not np.isfinite(a).all():
        raise ValueError('Input contains nonfinite values.')
    return a.astype(np.result_type(a.dtype, np.float32), copy=False)


def _scores(q: np.ndarray, c: np.ndarray, metric: str) -> np.ndarray:
    if metric == 'l2':
        # Squared Euclidean distance, without an N x V x d temporary.
        d = (q*q).sum(1)[:, None] + (c*c).sum(1)[None, :] - 2*q@c.T
        return np.maximum(d, 0)
    if metric == 'cosine':
        qn = np.linalg.norm(q, axis=1, keepdims=True)
        cn = np.linalg.norm(c, axis=1, keepdims=True)
        if np.any(qn == 0) or np.any(cn == 0):
            raise ValueError('Cosine distance is undefined for zero vectors.')
        return 1 - (q/qn)@(c/cn).T
    raise ValueError("metric must be 'l2' or 'cosine'")


def nearest_rows(
    queries: np.ndarray, candidates: np.ndarray, k: int = 1,
    metric: str = 'l2', block_size: int = 128,
) -> tuple[np.ndarray, np.ndarray]:
    """Return candidate row IDs and scores, each with shape (N, k).

    L2 scores are squared distances. All candidate rows are searched.
    Sorting ties follow original candidate order. This is exact blockwise NN,
    not an approximate-nearest-neighbor index.
    """
    q, c = _matrix(queries), _matrix(candidates)
    if q.shape[1] != c.shape[1] or not 1 <= k <= len(c) or block_size < 1:
        raise ValueError('Incompatible dimensions, k, or block_size.')
    ids = np.empty((len(q), k), dtype=np.int64)
    values = np.empty((len(q), k), dtype=np.result_type(q.dtype, c.dtype))
    for start in range(0, len(q), block_size):
        stop = min(start+block_size, len(q))
        d = _scores(q[start:stop], c, metric)
        order = np.argsort(d, axis=1, kind='stable')[:, :k]
        ids[start:stop] = order
        values[start:stop] = np.take_along_axis(d, order, axis=1)
    return ids, values


def nth_neighbor(
    queries: np.ndarray, candidates: np.ndarray, rank: int,
    block_size: int = 128,
) -> np.ndarray:
    """Return the rank-th nearest candidate (rank is one-based).

    For SGT MRP, rank must be estimated on independent calibration pairs.
    rank=len(candidates) gives the farthest neighbor.
    """
    q, c = _matrix(queries), _matrix(candidates)
    if q.shape[1] != c.shape[1] or not 1 <= rank <= len(c) or block_size < 1:
        raise ValueError('Incompatible dimensions, rank, or block_size.')
    out = np.empty(len(q), dtype=np.int64)
    for start in range(0, len(q), block_size):
        d = _scores(q[start:start+block_size], c, 'l2')
        out[start:start+len(d)] = np.argsort(d, axis=1, kind='stable')[:, rank-1]
    return out


def coordinate_difference(vectors: np.ndarray) -> np.ndarray:
    e = _matrix(vectors)
    return e - np.roll(e, 1, axis=1)


def ednn_mapping(original: np.ndarray, obfuscated: np.ndarray) -> np.ndarray:
    """Map every obfuscated row to an original row using coordinate differences.

    The exact guarantee applies to row-specific offsets c_i * ones, possibly
    followed by a row permutation. It does not cover arbitrary rotations.
    """
    ids, _ = nearest_rows(coordinate_difference(obfuscated),
                          coordinate_difference(original))
    return ids[:, 0]


def sorted_row_mapping(original: np.ndarray, observed: np.ndarray) -> np.ndarray:
    """For Y=P X Q, recover original-row IDs for observed rows by row sorting.

    Independent NN can collide under noise. This function does not enforce a
    global bijection; use an assignment solver when that constraint is needed.
    """
    ids, _ = nearest_rows(np.sort(_matrix(observed), axis=1),
                          np.sort(_matrix(original), axis=1))
    return ids[:, 0]


def majority_mapping(layer_maps: np.ndarray, vocab_size: int) -> np.ndarray:
    maps = np.asarray(layer_maps)
    if maps.ndim != 2 or not np.issubdtype(maps.dtype, np.integer):
        raise ValueError('Expected integer mappings with shape (layers, observed_rows).')
    if not len(maps) or vocab_size < 1 or np.any(maps < 0) or np.any(maps >= vocab_size):
        raise ValueError('Empty layers or invalid candidate IDs.')
    return np.asarray([np.bincount(maps[:, i], minlength=vocab_size).argmax()
                       for i in range(maps.shape[1])])


def gate_fingerprint(projected_tables: Sequence[np.ndarray]) -> np.ndarray:
    """Stack per-row means of E @ W_gate from multiple layers."""
    if not projected_tables:
        raise ValueError('Provide at least one projected table.')
    tables = [_matrix(t) for t in projected_tables]
    if len({len(t) for t in tables}) != 1:
        raise ValueError('All tables must use the same vocabulary rows.')
    return np.stack([t.mean(axis=1) for t in tables], axis=1)


def attention_fingerprint(projected_block: np.ndarray) -> np.ndarray:
    """Return q_i (Q.T Q)^-1 q_i.T for a full-column-rank block Q.

    Q -> P Q A preserves the fingerprint up to P for invertible A. No ridge
    term is silently added: a ridge would change the exact invariant for
    general nonorthogonal A.
    """
    q = _matrix(projected_block).astype(np.float64)
    if np.linalg.matrix_rank(q) != q.shape[1]:
        raise ValueError('The exact inverse formula requires full column rank.')
    solved = np.linalg.solve(q.T@q, q.T).T
    return np.einsum('ij,ij->i', q, solved)


def frequency_rank_mapping(prior_counts: np.ndarray, observed_counts: np.ndarray) -> np.ndarray:
    """Match descending frequency ranks; output observed ID -> original ID.

    A fixed one-to-one substitution and comparable plaintext distributions
    are assumptions, not guaranteed by the function. Ties follow ID order.
    """
    p, q = np.asarray(prior_counts), np.asarray(observed_counts)
    if p.ndim != 1 or p.shape != q.shape or np.any(p < 0) or np.any(q < 0):
        raise ValueError('Provide same-sized nonnegative count vectors.')
    original_order = np.argsort(-p.astype(float), kind='stable')
    observed_order = np.argsort(-q.astype(float), kind='stable')
    mapping = np.empty(len(p), dtype=np.int64)
    mapping[observed_order] = original_order
    return mapping


@dataclass
class PrefixMatchResult:
    tokens: np.ndarray
    matched_rows: np.ndarray
    distances: np.ndarray


def greedy_prefix_match(
    observed: np.ndarray, vocab_size: int,
    forward_last: Callable[[list[int]], np.ndarray], *,
    candidate_order: Callable[[list[int]], Iterable[int]] | None = None,
    sort_features: bool = False, permuted_rows: bool = False,
    epsilon: float | None = None,
) -> PrefixMatchResult:
    """Core L1 prefix matching, with hidden/sequence permutation variants.

    forward_last(prefix) must implement the actual target prefix computation
    and return its final-position hidden vector, including template/positions.
    The callback owns model/KV-cache handling. candidate_order must enumerate
    the full vocabulary; epsilon allows the paper's approximate early accept.
    This reference is deliberately unbatched and is not a full LLM runner.
    """
    h = _matrix(observed)
    if vocab_size < 1 or (epsilon is not None and epsilon < 0):
        raise ValueError('Invalid vocabulary size or threshold.')
    comparison = np.sort(h, axis=1) if sort_features else h
    remaining = list(range(len(h)))
    tokens, row_ids, distances = [], [], []
    for i in range(len(h)):
        order = list(candidate_order(tokens) if candidate_order else range(vocab_size))
        if len(order) != vocab_size or set(order) != set(range(vocab_size)):
            raise ValueError('candidate_order must be a full vocabulary permutation.')
        rows = remaining if permuted_rows else [i]
        best = (float('inf'), None, None)
        for token in order:
            vector = np.asarray(forward_last(tokens+[int(token)]))
            if vector.shape != (h.shape[1],) or not np.isfinite(vector).all():
                raise ValueError('forward_last returned an incompatible hidden state.')
            if sort_features:
                vector = np.sort(vector)
            d = np.abs(comparison[rows]-vector).sum(axis=1)
            pos = int(d.argmin())
            if float(d[pos]) < best[0]:
                best = (float(d[pos]), int(token), rows[pos])
            if epsilon is not None and float(d[pos]) < epsilon:
                break
        distance, token, row = best
        tokens.append(token)
        row_ids.append(row)
        distances.append(distance)
        if permuted_rows:
            remaining.remove(row)
    return PrefixMatchResult(np.asarray(tokens, dtype=np.int64),
                             np.asarray(row_ids, dtype=np.int64),
                             np.asarray(distances))


def labels_from_logit_gradient(gradient: np.ndarray) -> np.ndarray:
    """Hard-label, unweighted softmax-CE logits gradient: g=p-onehot(y).

    This does not recover labels directly from arbitrary earlier-layer or
    aggregated gradients, nor assume that labels are available at inference.
    """
    return np.argmin(_matrix(gradient), axis=1)


def run_self_checks() -> dict[str, object]:
    rng = np.random.default_rng(20261112)
    embedding = rng.normal(size=(23, 9))
    ids = np.array([2, 8, 1, 16, 4])
    assert np.array_equal(nearest_rows(embedding[ids], embedding)[0][:, 0], ids)

    # A deliberately poor NN case: antipodal unit vectors. Farthest recovery
    # succeeds, demonstrating why SGT's MRP tests more than nearest neighbors.
    unit = embedding/np.linalg.norm(embedding, axis=1, keepdims=True)
    assert np.array_equal(nth_neighbor(-unit[ids], unit, len(unit)), ids)

    perm = rng.permutation(len(embedding))
    shifted = embedding[perm] + rng.normal(0, 25, (len(embedding), 1))
    assert np.array_equal(ednn_mapping(embedding, shifted), perm)
    rotation, _ = np.linalg.qr(rng.normal(size=(9, 9)))
    assert not np.allclose(coordinate_difference(embedding@rotation),
                           coordinate_difference(embedding))

    x = rng.normal(size=(23, 13))
    column_perm = rng.permutation(x.shape[1])
    y = x[perm][:, column_perm]
    assert np.array_equal(sorted_row_mapping(x, y), perm)
    aligned_y = y[np.argsort(perm)]
    assert np.array_equal(nearest_rows(aligned_y.T, x.T)[0][:, 0], column_perm)
    noisy_vote = np.stack([perm, perm, np.roll(perm, 1)])
    assert np.array_equal(majority_mapping(noisy_vote, len(perm)), perm)

    g2 = rng.normal(size=(23, 7))
    plain_gate = gate_fingerprint([x, g2])
    cipher_gate = gate_fingerprint([y, g2[perm][:, rng.permutation(7)]])
    assert np.allclose(cipher_gate, plain_gate[perm], atol=1e-12)

    q = rng.normal(size=(23, 5))
    a = rng.normal(size=(5, 5))+3*np.eye(5)
    fingerprint = attention_fingerprint(q)
    assert np.allclose(attention_fingerprint(q[perm]@a), fingerprint[perm], atol=1e-10)
    # Unknown additive noise breaks the exact statement; no universal security
    # claim is inferred from the noiseless invariant.
    assert not np.allclose(attention_fingerprint(q[perm]@a+rng.normal(0, .2, q.shape)),
                           fingerprint[perm], atol=1e-8)

    counts = rng.permutation(np.arange(1, 24))*10
    assert np.array_equal(frequency_rank_mapping(counts, counts[perm]), perm)

    def causal_last(prefix: list[int]) -> np.ndarray:
        prior = embedding[prefix[:-1]].sum(0) if len(prefix) > 1 else np.zeros(9)
        return embedding[prefix[-1]] + .173*prior + .01*len(prefix)*np.arange(9)

    h = np.stack([causal_last(ids[:i+1].tolist()) for i in range(len(ids))])
    decoded = greedy_prefix_match(h, len(embedding), causal_last)
    assert np.array_equal(decoded.tokens, ids)
    hidden_permuted = np.stack([v[rng.permutation(9)] for v in h])
    shuffled = hidden_permuted[rng.permutation(len(h))]
    decoded = greedy_prefix_match(shuffled, len(embedding), causal_last,
                                  sort_features=True, permuted_rows=True, epsilon=1e-10)
    assert np.array_equal(decoded.tokens, ids)

    logits = rng.normal(size=(len(ids), len(embedding)))
    probabilities = np.exp(logits-logits.max(1, keepdims=True))
    probabilities /= probabilities.sum(1, keepdims=True)
    grad = (probabilities-np.eye(len(embedding))[ids])/len(ids)
    assert np.array_equal(labels_from_logit_gradient(grad), ids)
    return {
        'nearest_rows': 'PASS', 'MRP_antipodal_case': 'PASS', 'EDNN_offset_invariant': 'PASS',
        'EDNN_rotation_boundary': 'PASS', 'weight_row_and_column_mapping': 'PASS',
        'multi_layer_voting': 'PASS', 'gate_invariant': 'PASS',
        'attention_general_invertible_invariant': 'PASS', 'attention_noise_boundary': 'PASS',
        'frequency_mapping': 'PASS', 'causal_prefix_and_permutation_variants': 'PASS',
        'softmax_CE_logit_labels': 'PASS',
        'scope': 'Synthetic algebra/algorithm checks only; no real LLM experiments.',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-check', action='store_true')
    args = parser.parse_args()
    if args.self_check:
        import json
        print(json.dumps(run_self_checks(), indent=2))
    else:
        parser.print_help()
