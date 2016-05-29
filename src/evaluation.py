# coding: utf-8

from __future__ import division
from __future__ import print_function
from __future__ import with_statement

import pro
from nltk.translate.bleu_score import corpus_bleu
from operator import itemgetter
import sys


def best_reranking(inputs, candidates, classifier, pca, limit=1000):
    """
    Returns a list of the best sentences according to the reranking
    Only the top sentence is returned
    """
    sentences = []
    classifications = 0

    for i, input in enumerate(inputs):

        results = []

        sys.stdout.write("\rReranking %6.2f%% classifications: %d" % ((100 * i) / float(len(inputs)), classifications))
        sys.stdout.flush()

        for j in range(0, min(limit, len(candidates[i]))):

            score = 0
            candidate1 = candidates[i][j]

            for k in range(0, min(limit, len(candidates[i]))):
                if k != j:
                    candidate2 = candidates[i][k]
                    classifications += 1
                    if classifier.predict(pca.transform([pro.feature_vector(input, candidate1, candidate2)])) != [-1]:
                        score += 1

            result = (score, candidate1[1])
            results.append(result)

        results = sorted(results, key=itemgetter(0), reverse=True)
        (_, target) = results[0]
        sentences.append(target)

    print("\rReranking 100%% classifications: %d" % classifications)

    return sentences


def best_baseline(inputs, candidates):
    """
    Returns a list of the best sentences according to the baseline, i.e. the phrase based model
    """
    sentences = []

    for i, input in enumerate(inputs):
        (_, target, _) = candidates[i][0]
        sentences.append(target)

    return sentences


def print_evaluation(inputs, references, candidates, classifier, pca, limit=1000):
    bleu_references = [[x] for x in references]
    bleu_hypotheses_baseline = best_baseline(inputs, candidates)

    baseline_blue = corpus_bleu(bleu_references, bleu_hypotheses_baseline)
    print("Baseline BLEU: %0.10f" % baseline_blue)

    bleu_hypotheses_reranking = best_reranking(inputs, candidates, classifier, pca, limit)
    reranking_blue = corpus_bleu(bleu_references, bleu_hypotheses_reranking)
    print("Reranking BLEU: %0.10f" % reranking_blue)