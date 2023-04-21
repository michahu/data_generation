from utils import data_generator
from utils.constituent_building import *
from utils.conjugate import *
from utils.randomize import choice
from utils.vocab_sets_dynamic import *


class FourthWordThatGenerator(data_generator.Generator):
    def __init__(self, pct_restrictive_relative=0.6, uid="fourth_word_that"):
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

        if random.random() < self.pct_restrictive_relative:
            adjective = choice(self.adjectives)
            relative_clause = "%s %s" % (linking_verb, adjective[0])
        else:
            transitive_verb = choice(self.transitive_verbs)
            obj = choice(self.nominals)
            art = choice(get_matched_by(obj, "arg_1", self.articles))

            if art[0] == "":
                relative_clause = "%s %s %s" % (
                    linking_verb,
                    transitive_verb[0],
                    obj[0],
                )
            else:
                relative_clause = "%s %s %s %s" % (
                    linking_verb,
                    transitive_verb[0],
                    art[0],
                    obj[0],
                )

        return relative_clause, linguistic

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
        fourth_word_that = False
        a1 = choice(self.starting_articles)[0]

        if random.random() < 0.75:
            adj = choice(self.adjectives)
            a1 += " " + adj[0]
            fourth_word_that = True

            if random.random() < 0.33:
                adj = choice(self.adjectives)
                a1 += " " + adj[0]
                fourth_word_that = False

        n1 = choice(get_matches_of(a1, "arg_1", self.nominals))
        relative_clause, linguistic = self.make_relative_clause()

        if random.random() < 0.5:
            # wh = choice(get_matched_by(n1, "arg_1", get_all_wh_words()))
            rc1, _ = self.make_relative_clause()
            # print(
            #     f"article 1: {a1[0]} \nsubject: {n1[0]} \nrelative clause: {rc1} \nrelative clause 2: {relative_clause}"
            # )
            sentence = "%s %s that %s %s." % (
                a1,
                n1[0],
                rc1,
                relative_clause,
            )

        else:
            # print(
            #     f"article 1: {a1[0]} \nsubject: {n1[0]} \nrelative clause: {relative_clause}"
            # )
            sentence = "%s %s %s." % (a1, n1[0], relative_clause)
            # print(data)

        data = {
            "surface": str(int(fourth_word_that)),
            "linguistic": linguistic,
        }

        data["sentence"] = sentence
        return data, data["sentence"]


if __name__ == "__main__":
    generator = FourthWordThatGenerator()
    generator.generate_paradigm(
        rel_output_path="outputs/%s_raw.jsonl" % generator.uid,
        number_to_generate=50000,
    )
    # print(generator.sample())
