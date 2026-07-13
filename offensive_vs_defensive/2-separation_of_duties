# Separation of Duties: No Single Person Should Hold the Keys

*Part 2 of the "Offensive vs Defensive Security" series*

## One Person, One Point of Failure

Imagine a single engineer who can write code, approve their own pull request, deploy it to production, and review the logs afterward — with no one else in the loop at any stage. Nothing about that setup requires malicious intent to go wrong. A mistake slips through unchecked. And if that engineer's intent *were* malicious, or their credentials were compromised, nothing would stand in the way.

That's the exact failure mode **Separation of Duties (SoD)** is designed to prevent. The principle is simple: critical tasks should be split across multiple people or systems so that no single individual has enough control to cause serious harm — whether by error, negligence, or deliberate abuse — without someone else noticing.

We've already covered Defense in Depth and Least Privilege in this series. SoD is the natural next layer: even with minimal privileges, concentrating the *wrong combination* of privileges in one place recreates the same risk.

## Rooted in Accounting, Adopted by Security

Separation of Duties didn't start in IT — it started in finance. Traditional accounting controls have long required that the person who authorizes a payment isn't the same person who executes it or reconciles the books. This isn't about distrust of any one employee; it's about designing a system where collusion or error requires more than one point of failure to succeed.

As IT systems became the backbone of financial and operational processes, security teams adapted the same logic: split authority, require independent verification, and never let one identity — human or automated — hold end-to-end control over a sensitive process.

## Why SoD Matters

- **Reduces insider threat.** Most insider risk isn't dramatic sabotage — it's an employee with more access than their role justifies, combined with no oversight. SoD makes unilateral misuse structurally harder, not just policy-discouraged.
- **Improves accountability.** When tasks are divided, actions are traceable to specific individuals at specific stages, making audits meaningful rather than symbolic.
- **Catches errors before they compound.** A second set of eyes on a configuration change or a financial transaction catches mistakes that a single person, however careful, will eventually miss.
- **Strengthens regulatory compliance.** Frameworks like SOX, PCI-DSS, and ISO 27001 explicitly require SoD controls in relevant processes — this isn't optional in regulated industries.

## Applying SoD in IT Security

**Administrative privileges**: The person who requests elevated access shouldn't be the person who approves it. Approval and provisioning should sit with a separate role or an automated policy engine.

**Change management**: Developers write code; a separate reviewer approves it; a distinct deployment pipeline (ideally automated, not manually triggered by the developer) pushes it to production. No individual should be able to single-handedly move code from laptop to live environment.

**Incident response**: The analyst who detects an incident shouldn't be solely responsible for both containment *and* the after-action report validating their own response was adequate. Independent review closes the loop.

**Financial and procurement systems**: Anyone provisioning cloud infrastructure with real cost implications shouldn't also control the billing approval process — a control point that matters more than it sounds, especially as cloud spend scales.

## Challenges in Fast-Moving Environments

SoD's biggest enemy is speed. Startups and agile teams often resist splitting duties because it feels like it slows delivery — and to some extent, it does, by design.

**Challenge: Small teams, overlapping roles.** In lean organizations, the same person often wears multiple hats out of necessity. *Mitigation:* where full separation isn't feasible, compensate with detective controls — logging, monitoring, and periodic review — rather than abandoning the principle entirely.

**Challenge: Perceived bureaucracy.** Engineers resist approval gates that feel like friction for its own sake. *Mitigation:* automate SoD enforcement wherever possible — RBAC policies, mandatory pull-request approvals, and pipeline gates that block self-approval by default, rather than relying on manual policy adherence.

**Challenge: Shadow access.** Employees find workarounds when formal processes feel too slow. *Mitigation:* pair SoD with usable, fast-tracked approval workflows so the compliant path is also the convenient one.

## A Familiar Scenario

Consider a common (and avoidable) failure pattern: a single administrator holds both the ability to create new user accounts *and* the ability to approve access requests for those accounts. If that credential is compromised — or misused — an attacker or bad actor can create a new privileged account and approve their own request, with no second party involved at any stage. Organizations that catch this gap typically do so through access reviews that specifically hunt for self-approving workflows, not through the controls that were originally in place. It's a pattern worth auditing for directly rather than assuming it doesn't exist.

## Visualizing SoD in a Deployment Workflow

```
Without SoD:   [ Developer ] -> writes, approves, and deploys code alone

With SoD:      [ Developer ] -> writes code
                    |
               [ Reviewer ]  -> approves change
                    |
               [ Pipeline ]  -> automated deployment (no manual override)
```

A flowchart like this — mapped to your organization's actual access-request or deployment process — is an effective way to make SoD concrete for readers rather than abstract.

## Closing Thoughts

Separation of Duties won't stop every threat on its own, but it removes one of the most exploitable conditions in any system: unchecked, concentrated control. Combined with Least Privilege and layered defenses, it forms a core part of a mature security posture — one built to assume that any single person or system, however trusted, can fail or be compromised.

Where has your organization struggled to implement SoD without slowing everything down? Drop your experience in the comments — this is a principle everyone agrees with in theory and constantly negotiates in practice.

**Next up in the series:** we shift focus to the other side of the equation entirely — how attackers think, plan, and exploit the gaps these controls are meant to close.

---

*This is Part 2 of a 6-part series on Offensive vs Defensive Security.*
