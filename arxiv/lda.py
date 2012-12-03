__all__ = [u"LDA"]

import numpy as np
from scipy.special import gammaln, psi

from .text_utils import tokenize_document


def dir_expect(alpha):
    if len(alpha.shape) == 1:
        return psi(alpha) - psi(np.sum(alpha))
    return psi(alpha) - psi(np.sum(alpha, axis=-1))[:, None]


class LDA:

    def __init__(self, vocab, ntopics, ndocs, alpha, eta, delay, rate):
        self.vocab = list(vocab)
        self.K = ntopics
        self.W = len(self.vocab)
        self.D = ndocs
        self.alpha = alpha
        self.eta = eta
        self.tau = delay
        self.kappa = rate

        self.lam = np.random.gamma(100.0, 0.01, (self.W, self.K))
        self.Elogbeta = dir_expect(self.lam)
        self.expElogbeta = np.exp(self.Elogbeta)

        self.tstep = 0

    def _expectation(self, docs, maxiter=100, tol=0.0001, eps=1e-100):
        docs = [tokenize_document(d, vocab=self.vocab) for d in docs]
        size = len(docs)
        gamma = np.random.gamma(100.0, 0.01, (size, self.K))
        expElogth = np.exp(dir_expect(gamma))
        stats = np.zeros_like(self.lam)

        for i, doc in enumerate(docs):
            try:
                word_ids, word_counts = zip(*[w for w in doc.iteritems()])
            except ValueError:
                continue
            word_ids = np.array(word_ids, dtype=int)
            word_counts = np.array(word_counts, dtype=int)
            gamma_d = gamma[i]
            expElogth_d = expElogth[i]
            expElogbeta_d = self.expElogbeta[word_ids]
            norm = np.dot(expElogth_d, expElogbeta_d.T) + eps
            for j in range(maxiter):
                gamma0 = gamma
                gamma_d = self.alpha + expElogth_d * np.dot(
                                word_counts / norm, expElogbeta_d)
                expElogth_d = np.exp(dir_expect(gamma_d))
                norm = np.dot(expElogbeta_d, expElogth_d) + eps

                delta = np.mean(np.abs(gamma_d - gamma0))
                if delta < tol:
                    break
            gamma[i] = gamma_d
            stats[word_ids] += np.outer(word_counts / norm, expElogth_d)

        stats *= self.expElogbeta

        return gamma, stats, docs

    def update(self, docs, **kwargs):
        rho = (self.tau + self.tstep) ** -self.kappa
        gamma, stats, docs = self._expectation(docs, **kwargs)
        bound = self.approx_bound(docs, gamma, preprocess=False)

        # Update lambda.
        self.lam = self.lam * (1.0 - rho) + rho * (self.eta
                                            + self.D * stats / len(docs))
        self.Elogbeta = dir_expect(self.lam)
        self.expElogbeta = np.exp(self.Elogbeta)
        self.tstep += 1

        return gamma, self.lam, bound

    def approx_bound(self, docs, gamma, preprocess=True):
        if preprocess:
            docs = [tokenize_document(d, vocab=self.vocab) for d in docs]

        Elogth = dir_expect(gamma)

        score = 0.0
        fullnorm = 0.0

        for i, doc in enumerate(docs):
            try:
                word_ids, word_counts = zip(*[w for w in doc.iteritems()])
            except ValueError:
                continue
            word_ids = np.array(word_ids, dtype=int)
            word_counts = np.array(word_counts, dtype=int)
            norm = np.zeros(len(word_ids))
            for j in range(len(word_ids)):
                tmp = Elogth[i] + self.Elogbeta[word_ids[j]]
                tmax = np.max(tmp)
                norm[j] = np.log(sum(np.exp(tmp - tmax))) + tmax
            score += np.sum(word_counts * norm)
            fullnorm += np.sum(word_counts)

        score += np.sum((self.alpha - gamma) * Elogth)
        score += np.sum(gammaln(gamma) - gammaln(self.alpha))
        score += np.sum(gammaln(self.alpha * self.K) -
                        gammaln(np.sum(gamma, axis=1)))

        score *= self.D / len(docs)

        score += np.sum((self.eta - self.lam) * self.Elogbeta)
        score += np.sum(gammaln(self.lam) - gammaln(self.eta))
        score += np.sum(gammaln(self.eta * self.W) -
                        gammaln(np.sum(self.lam, axis=1)))

        return score * len(docs) / fullnorm / self.D
