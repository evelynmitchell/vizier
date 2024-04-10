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

"""Decorators for Policy.suggest."""

import functools
import types
from typing import TypeVar
import attrs
from vizier._src.pythia.policy import Policy
from vizier._src.pythia.policy import SuggestDecision
from vizier._src.pythia.policy import SuggestRequest
from vizier._src.pyvizier.shared import parameter_iterators as pi
from vizier._src.pyvizier.shared import trial


_T = TypeVar('_T')


def seed_with_default(suggest_fn: _T) -> _T:
  """Decorator for Policy.suggest to always suggest the default or center.

  How to use as a decorator:

  ```
  class MyPolicy(Policy):
    @seed_with_default
    def suggest(self, ...):
      ...
  ```

  How to use as a function:
  class MyPolicy(Policy):

    def __init__(self, ..., *, use_seed_with_default: bool):
      if use_seed_with_default:
        self.suggest = seed_with_default(self.suggest)

    def suggest(self, ...):
      ...

  Args:
    suggest_fn:

  Returns:
    suggest_fn that suggest the default or center of the search space if
    the study is empty.
  """

  if hasattr(suggest_fn, '__self__'):
    unbound = seed_with_default(suggest_fn.__func__)
    return types.MethodType(unbound, suggest_fn.__self__)

  @functools.wraps(suggest_fn)
  def wrapper_fn(self: Policy, request: SuggestRequest) -> SuggestDecision:
    """If study is empty, suggests a default trial before using the policy."""
    if request.max_trial_id > 0:
      return suggest_fn(self, request)

    default_parameters = pi.get_default_parameters(
        request.study_config.search_space
    )
    decision = SuggestDecision([trial.TrialSuggestion(default_parameters)])

    if request.count > 1:
      more_suggestions = suggest_fn(
          self, attrs.evolve(request, count=request.count - 1)
      )
      decision.suggestions.extend(more_suggestions.suggestions)
      decision.metadata = more_suggestions.metadata

    return decision

  return wrapper_fn
