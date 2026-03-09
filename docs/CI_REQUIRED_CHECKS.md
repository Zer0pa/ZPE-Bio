# CI Required Checks Recommendation

Date: 2026-02-20

Recommended branch protection for `main`:

1. Require pull request before merge.
2. Require status checks to pass before merge.
3. Require branches to be up to date before merge.
4. Dismiss stale approvals on new commits.

Required status checks:

1. `CI Python / lint-test-build (ubuntu-latest, 3.10)`
2. `CI Python / lint-test-build (ubuntu-latest, 3.11)`
3. `CI Python / lint-test-build (macos-latest, 3.10)`
4. `CI Python / lint-test-build (macos-latest, 3.11)`
5. `CI Rust / rust-quality (ubuntu-latest)`
6. `CI Rust / rust-quality (macos-latest)`

Optional but recommended:

1. `CI Python / build-artifacts`
2. `Release Skeleton / package` (manual release rehearsal)
