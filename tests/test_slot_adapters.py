import copy
import unittest

from comfyui.slot_adapters import SLOT_ADAPTERS, prepare_slot_plan


class TestSlotAdapter(unittest.TestCase):
    def setUp(self):
        config = SLOT_ADAPTERS["anima-base-v1"]
        self.slots = [{"address": a} for a in config["slots"].values()]
        self.slots += [{"address": a, "current_value": v}
                       for a, v in config["models"].items()]
        self.source = {"shot_id": "shot_la_pomme_01_01", "prompt_id": "image_qwen_shot_la_pomme_01_01",
                       "model": "qwen-image", "status": "draft",
                       "prompt": "Canonical prompt", "negative_prompt": "No extra cats"}

    def plan(self, **kwargs):
        return prepare_slot_plan(self.source, self.slots, test_model="anima-base-v1",
                                 seed=10040101, filename_prefix="la-pomme/test/shot_la_pomme_01_01",
                                 **kwargs)

    def test_typed_injection_and_provenance_without_mutation(self):
        before = copy.deepcopy((self.source, self.slots))
        plan = self.plan()
        overrides = {o["address"]: o["value"] for o in plan["overrides"]}
        self.assertEqual(overrides["90.text"], self.source["prompt"])
        self.assertEqual(overrides["90.text_1"], self.source["negative_prompt"])
        self.assertEqual(overrides["91.megapixels"], 0.589824)
        self.assertIs(type(overrides["90.seed"]), int)
        self.assertIs(overrides["90.value"], True)
        self.assertEqual(plan["source_model"], "qwen-image")
        self.assertEqual(plan["test_model"], "anima-base-v1")
        self.assertEqual((self.source, self.slots), before)

    def test_missing_mapping_fails_closed(self):
        self.slots.pop(0)
        with self.assertRaises(ValueError):
            self.plan()

    def test_model_drift_fails_closed(self):
        self.slots[-1]["current_value"] = "different.safetensors"
        with self.assertRaises(ValueError):
            self.plan()

    def test_linked_slot_fails_closed(self):
        self.slots[0]["linked_from"] = 10
        with self.assertRaises(ValueError):
            self.plan()

    def test_oversized_dimensions_fail_closed(self):
        with self.assertRaises(ValueError):
            self.plan(width=1280, height=720)

    def test_non_16_9_dimensions_fail_closed(self):
        with self.assertRaises(ValueError):
            self.plan(width=512, height=512)

    def test_explicit_portrait_and_non_turbo(self):
        self.source.update(aspect_ratio="9:16", turbo=False)
        plan = self.plan(width=576, height=1024, aspect_ratio="9:16")
        overrides = {o["address"]: o["value"] for o in plan["overrides"]}
        self.assertEqual(overrides["91.aspect_ratio"], "9:16 (Portrait Widescreen)")
        self.assertEqual(overrides["91.megapixels"], 0.589824)
        self.assertIs(overrides["90.value"], False)
        self.assertEqual(plan["requested_aspect_ratio"], "9:16")

    def test_portrait_requires_explicit_ratio(self):
        with self.assertRaises(ValueError):
            self.plan(width=576, height=1024)

    def test_source_ratio_conflict_rejected(self):
        self.source["aspect_ratio"] = "16:9"
        with self.assertRaises(ValueError):
            self.plan(width=576, height=1024, aspect_ratio="9:16")

    def test_unsupported_ratio_rejected(self):
        with self.assertRaises(ValueError):
            self.plan(width=512, height=512, aspect_ratio="1:1")

    def test_non_boolean_turbo_rejected(self):
        with self.assertRaises(ValueError):
            self.plan(turbo="false")

    def test_source_false_turbo_cannot_be_silently_overridden(self):
        self.source["turbo"] = False
        with self.assertRaises(ValueError):
            self.plan(turbo=True)

    def test_nested_source_false_turbo_is_respected(self):
        self.source["source_adapter"] = {"turbo": False}
        self.assertIs(self.plan()["turbo"], False)

    def test_inconsistent_source_turbo_rejected(self):
        self.source.update(turbo=False, source_adapter={"turbo": True})
        with self.assertRaises(ValueError):
            self.plan()

    def test_discovered_ratio_enum_checked(self):
        for slot in self.slots:
            if slot["address"] == "91.aspect_ratio":
                slot["enum"] = ["16:9 (Widescreen)"]
        with self.assertRaises(ValueError):
            self.plan(width=576, height=1024, aspect_ratio="9:16")


if __name__ == "__main__":
    unittest.main()
