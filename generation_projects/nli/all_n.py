from utils import data_generator
from utils.conjugate import *
from utils.constituent_building import *
from utils.conjugate import *
from utils.randomize import choice
from utils.string_utils import string_beautify
import inflect
from utils.embed import *

class BothGenerator(data_generator.PresuppositionGenerator):
    def __init__(self):
        super().__init__(
            uid="all_n_presupposition"
        )
        self.safe_nouns = np.setdiff1d(all_plural_nouns, all_proper_names)


    def sample(self):
        # All three cats that like mice sleep

        D = random.choice(["all", "the"])
        number_inflector = inflect.engine()
        n = random.randint(2, 10)
        Num = number_inflector.number_to_words(n)
        Num_plus = number_inflector.number_to_words(n + 1)

        V = choice(all_possibly_plural_verbs)
        V_bare = get_bare_form(V)
        N_subj = choice(get_matches_of(V, "arg_1", self.safe_nouns))
        N_subj_alt = choice(get_matches_of(V, "arg_1", self.safe_nouns), avoid=N_subj)
        V_args = verb_args_from_verb(V, subj=N_subj, allow_negated=False, allow_modal=False, allow_quantifiers=False)
        V_args = embed_V_args_under_modal(V_args)
        RC = verb_phrase_from_subj(N_subj)
        rel = choice(get_matched_by(N_subj, "arg_1", all_relativizers))
        V_neg, Aux_neg = negate_VP(V, V_args["aux"])

        unembedded_trigger = "%s %s %s %s %s %s %s %s." % (D, Num, N_subj[0], rel[0], RC[0], V_args["aux"][0], V_args["verb"][0], join_args(V_args["args"]))
        negated_trigger = "%s %s %s %s %s %s %s %s." % (D, Num, N_subj[0], rel[0], RC[0], Aux_neg[0], V_neg[0], join_args(V_args["args"]))
        if V_args["aux_under_modal"] == None:
            modal_trigger = "%s %s %s %s %s might %s %s." % (D, Num, N_subj[0], rel[0], RC[0], V_bare[0], join_args(V_args["args"]))
        else:
            modal_trigger = "%s %s %s %s %s might %s %s %s." % (D, Num, N_subj[0], rel[0], RC[0], V_args["aux_under_modal"][0], V_args["verb_under_modal"][0], join_args(V_args["args"]))
        conditional_trigger = "If %s %s %s %s %s %s %s %s, it's okay." % (D, Num, N_subj[0], rel[0], RC[0], V_args["aux"][0], V_args["verb"][0], join_args(V_args["args"]))

        if V["finite"] == "1":
            do = get_do_form(V)
            interrogative_trigger = "%s %s %s %s %s %s %s %s?" % (do[0], D, Num, N_subj[0], rel[0], RC[0], V_bare[0], join_args(V_args["args"]))
        else:
            interrogative_trigger = "%s %s %s %s %s %s %s %s?" % (V_args["aux"][0], D, Num, N_subj[0], rel[0], RC[0], V_args["verb"][0], join_args(V_args["args"]))

        presupposition = "there are exactly %s %s %s %s." % (Num, N_subj[0], rel[0], RC[0])
        if np.random.choice([True, False]):
            negated_options = ["there are exactly %s" % Num_plus,
                               "there are more than %s" % Num,
                               "there are dozens of"]
            negated_presupposition = "%s %s %s %s." % (np.random.choice(negated_options), N_subj[0], rel[0], RC[0])
        else:
            negated_presupposition = "there aren't exactly %s %s %s %s." % (Num, N_subj[0], rel[0], RC[0])
        neutral_presupposition = "there are exactly %s %s %s %s." % (Num, N_subj_alt[0], rel[0], RC[0])

        data = self.build_presupposition_paradigm(unembedded_trigger=unembedded_trigger,
                                                  negated_trigger=negated_trigger,
                                                  interrogative_trigger=interrogative_trigger,
                                                  modal_trigger=modal_trigger,
                                                  conditional_trigger=conditional_trigger,
                                                  presupposition=presupposition,
                                                  negated_presupposition=negated_presupposition,
                                                  neutral_presupposition=neutral_presupposition)
        return data, presupposition






generator = BothGenerator()
generator.generate_paradigm(number_to_generate=100, rel_output_path="outputs/IMPPRES/presupposition/%s.jsonl" % generator.uid)
