from utils import data_generator
from utils.constituent_building import *
from utils.conjugate import *
from utils.randomize import choice
from utils.vocab_sets_dynamic import *

import argparse


class ConfoundedArticleTenseGenerator(data_generator.Generator):
    def __init__(
        self,
        pct_restrictive_relative=0.6,
        uid="contains_the",
    ):
        super().__init__()
        self.uid = uid
        self.data_fields = ["sentence", "surface", "linguistic"]
        self.pct_restrictive_relative = pct_restrictive_relative

        # quantifiers

        starting_articles_str = ["a", "an", "the"]
        articles_str = starting_articles_str + [""]

        self.starting_articles = reduce(
            np.union1d,
            [
                get_all("expression", s, get_all_determiners())
                for s in starting_articles_str
            ],
        )
        self.articles = reduce(
            np.union1d,
            [get_all("expression", s, get_all_determiners()) for s in articles_str],
        )

        # get singular nominals
        self.nominals = get_all(
            "category_2", "N", get_all("sg", "1", get_all_nominals())
        )

        self.aux_verbs_str = ["is", "was"]
        self.transitive_verbs = np.intersect1d(
            get_all_transitive_verbs(), get_all_ing_verbs()
        )
        self.adjectives = get_all_adjectives()

    def make_relative_clause(self):
        linking_verb = choice(self.aux_verbs_str)
        linguistic = str(int(linking_verb == "is"))
        is_proper = False
        is_transitive = False

        if random.random() < self.pct_restrictive_relative:
            adjective = choice(self.adjectives)
            relative_clause = "%s %s" % (linking_verb, adjective[0])
        else:
            is_transitive = True
            transitive_verb = choice(self.transitive_verbs)
            obj = choice(self.nominals)
            art = choice(get_matched_by(obj, "arg_1", self.articles))

            if art[0] == "":
                relative_clause = "%s %s %s" % (
                    linking_verb,
                    transitive_verb[0],
                    obj[0],
                )
                is_proper = True
            else:
                relative_clause = "%s %s %s %s" % (
                    linking_verb,
                    transitive_verb[0],
                    art[0],
                    obj[0],
                )

        return relative_clause, linguistic, is_proper, is_transitive

    def make_metadata_dict(self):
        """
        (non token-specific metadata is in class fields, e.g. self.field=syntax)
        :param extra_metadata: token-specific metadata, e.g. one_prefix_word_1="the"
        :return: join metadata
        """
        metadata = {
            "UID": self.uid,
        }
        return metadata

    def sample(self):
        a1 = choice(self.starting_articles)
        n1 = choice(get_matches_of(a1, "arg_1", self.nominals))
        (
            relative_clause,
            linguistic,
            is_proper,
            is_transitive,
        ) = self.make_relative_clause()

        if random.random() < 0.5:
            (
                rc1,
                _,
                _,
                _,
            ) = self.make_relative_clause()
            if not is_proper and is_transitive and random.random() < 0.5:
                rc2, _, _, _ = self.make_relative_clause()
                sentence = "%s %s that %s %s that %s." % (
                    a1[0],
                    n1[0],
                    rc1,
                    relative_clause,
                    rc2,
                )
            else:
                sentence = "%s %s that %s %s." % (
                    a1[0],
                    n1[0],
                    rc1,
                    relative_clause,
                )

        else:
            sentence = "%s %s %s." % (a1[0], n1[0], relative_clause)

        if self.uid == "contains_the":
            surface = str(int("the" in sentence))
        elif self.uid == "first_word_the":
            surface = a1[0] == "the"
        else:
            raise ValueError("Invalid task: %s" % self.task)

        data = {
            "surface": surface,
            "linguistic": linguistic,
        }

        data["sentence"] = sentence
        return data, data["sentence"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_samples", type=int, required=True)
    parser.add_argument("--task", type=str, required=True)
    args = parser.parse_args()

    generator = ConfoundedArticleTenseGenerator(uid=args.task)
    generator.generate_paradigm(
        rel_output_path="outputs/%s_raw.jsonl" % generator.uid,
        number_to_generate=args.num_samples,
    )
    # print(generator.sample())
