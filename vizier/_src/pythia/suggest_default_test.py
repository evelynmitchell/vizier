# Copyright 2024 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from vizier import pyvizier as vz
from vizier._src.pythia import policy as pythia
from vizier._src.pythia import suggest_default

from absl.testing import absltest

space = vz.SearchSpace()
space.root.add_int_param('x', 0, 1000)

empty_study_descriptor = vz.StudyDescriptor(
    vz.ProblemStatement(space),
    guid='1',
    max_trial_id=0,
)


class SuggestDefaultTest(absltest.TestCase):

  def test_decorator(self):
    class FakeDecoratedPolicy(pythia.Policy):

      @suggest_default.seed_with_default
      def suggest(
          self, request: pythia.SuggestRequest
      ) -> pythia.SuggestDecision:
        if request.count != 2:
          raise ValueError(f'count must be 2. Was: {request.count}')
        if request._study_descriptor != empty_study_descriptor:
          raise ValueError('study_descriptor must match request')
        return pythia.SuggestDecision(
            [vz.TrialSuggestion({'x': 999}), vz.TrialSuggestion({'x': 1000})]
        )

      def early_stop(
          self, request: pythia.EarlyStopRequest
      ) -> pythia.EarlyStopDecisions:
        return pythia.EarlyStopDecisions()

    FakeDecoratedPolicy().suggest(
        pythia.SuggestRequest(count=3, study_descriptor=empty_study_descriptor)
    )

  def test_init_override(self):
    class FakeInitOverridePolicy(pythia.Policy):

      def __init__(self):
        self.suggest = suggest_default.seed_with_default(self.suggest)

      def suggest(
          self, request: pythia.SuggestRequest
      ) -> pythia.SuggestDecision:
        if request.count != 2:
          raise ValueError(f'count must be 2. Was: {request.count}')
        if request._study_descriptor != empty_study_descriptor:
          raise ValueError('study_descriptor must match request')
        return pythia.SuggestDecision(
            [vz.TrialSuggestion({'x': 999}), vz.TrialSuggestion({'x': 1000})]
        )

      def early_stop(
          self, request: pythia.EarlyStopRequest
      ) -> pythia.EarlyStopDecisions:
        return pythia.EarlyStopDecisions()

    FakeInitOverridePolicy().suggest(
        pythia.SuggestRequest(count=3, study_descriptor=empty_study_descriptor)
    )


if __name__ == '__main__':
  absltest.main()
