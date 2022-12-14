import json

from allennlp.common.testing import ModelTestCase

from tests import FIXTURES_ROOT


class ComposedSeq2SeqTest(ModelTestCase):
    def setup_method(self):
        super().setup_method()
        self.set_up_model(
            FIXTURES_ROOT / "generation" / "composed" / "experiment.json",
            FIXTURES_ROOT / "generation" / "seq2seq_copy.tsv",
        )

    def test_model_can_train_save_and_load(self):
        self.ensure_model_can_train_save_and_load(self.param_file, tolerance=1e-2)

    def test_bidirectional_model_can_train_save_and_load(self):

        param_overrides = json.dumps(
            {
                "model.encoder.bidirectional": True,
                "model.decoder.decoder_net.decoding_dim": 20,
                "model.decoder.decoder_net.bidirectional_input": True,
            }
        )
        self.ensure_model_can_train_save_and_load(
            self.param_file, tolerance=1e-2, overrides=param_overrides
        )

    def test_no_attention_model_can_train_save_and_load(self):
        param_overrides = json.dumps({"model.decoder.decoder_net.attention": None})
        self.ensure_model_can_train_save_and_load(
            self.param_file, tolerance=1e-2, overrides=param_overrides
        )

    def test_greedy_model_can_train_save_and_load(self):
        param_overrides = json.dumps({"model.decoder.beam_search.beam_size": 1})
        self.ensure_model_can_train_save_and_load(
            self.param_file, tolerance=1e-2, overrides=param_overrides
        )

    def test_decode_runs_correctly(self):
        self.model.eval()
        training_tensors = self.dataset.as_tensor_dict()
        output_dict = self.model(**training_tensors)
        decode_output_dict = self.model.make_output_human_readable(output_dict)
        # `make_output_human_readable` should have added a `predicted_tokens` field to
        # `output_dict`. Checking if it's there.
        assert "predicted_tokens" in decode_output_dict

        # The output of model.make_output_human_readable should still have 'predicted_tokens' after
        # using the beam search. To force the beam search, we just remove `target_tokens` from the
        # input tensors.
        del training_tensors["target_tokens"]
        output_dict = self.model(**training_tensors)
        decode_output_dict = self.model.make_output_human_readable(output_dict)
        assert "predicted_tokens" in decode_output_dict
