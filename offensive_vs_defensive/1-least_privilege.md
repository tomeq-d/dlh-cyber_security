# Least Privilege: Giving Access, Not Trust

*Part 1 of the "Offensive vs Defensive Security" series*

## The Simplest Rule Everyone Still Gets Wrong

Here's a question worth asking about your own organization: does every employee, service account, and application have access to *exactly* what it needs — no more, no less? For most companies, the honest answer is no. Access accumulates. Permissions get granted "just in case." Old roles never get revoked when responsibilities change.

That gap is exactly what the **Principle of Least Privilege (PoLP)** exists to close. In simple terms: every user, application, and system should operate with the minimum level of access required to do its job, and nothing beyond that. It sounds almost too obvious to be a security principle — until you realize how rarely it's actually enforced.

In our last post, we covered Defense in Depth — the idea that security works in layers. Least Privilege is one of the most important controls *within* those layers, because it directly shrinks what an attacker can do once they're inside.

## Why It Matters More Than It Seems

Excess privilege doesn't cause breaches by itself — but it turns small breaches into catastrophic ones. Attackers rarely walk in the front door with admin rights. They get a foothold through something ordinary: a phished credential, a misconfigured service account, a vulnerable endpoint. What happens next depends entirely on how much that compromised identity can touch.

This pattern shows up again and again in real-world incidents: a low-level account gets compromised, and because that account had far more access than its role required, the attacker moves laterally across the network, escalates privileges, and reaches sensitive systems that had nothing to do with the original entry point. The initial breach is rarely the headline — the blast radius is.

Least Privilege doesn't prevent the first compromise. It contains it.

## Applying Least Privilege Across Real Environments

- **Operating systems**: Standard users shouldn't run with local admin rights by default. Elevated access should be granted per-task, not per-person.
- **Databases**: Application accounts should have scoped permissions (read-only where possible) rather than broad database-owner rights just because it's convenient during development.
- **Network devices**: Router and switch configurations should limit who can make changes, with role-specific access instead of shared administrative credentials.
- **Cloud environments**: This is where Least Privilege matters most today. Cloud IAM policies are often over-permissioned by default — a single overly broad S3 bucket policy or an IAM role with wildcard permissions (`"Action": "*"`) can expose an entire environment. Cloud-native tools make it easy to grant broad access quickly; they don't make it easy to remember to scale it back.

## Challenges — and How to Overcome Them

Implementing Least Privilege sounds straightforward; doing it at scale is genuinely hard.

**Challenge: Access sprawl.** Permissions get granted reactively and rarely revoked. *Solution:* schedule regular access reviews and treat permission grants as time-bound, not permanent.

**Challenge: Operational friction.** Teams push back when tightened access slows down their work. *Solution:* pair Least Privilege with just-in-time (JIT) access — temporary elevation for specific tasks, automatically expiring afterward.

**Challenge: Visibility.** Many organizations simply don't know who has access to what. *Solution:* adopt Privileged Access Management (PAM) tools that centralize visibility, enforce approval workflows, and log privileged sessions for audit purposes.

**Challenge: Legacy systems.** Older infrastructure often wasn't designed with granular permissions in mind. *Solution:* isolate legacy systems behind stricter network segmentation to compensate where fine-grained access controls aren't possible.

## Practical Tips for Implementation

1. **Start with an access audit.** You can't reduce what you can't see. Map out who and what has access to which systems today.
2. **Adopt Role-Based Access Control (RBAC).** Define access by job function rather than granting permissions individually — it's easier to manage and audit.
3. **Automate de-provisioning.** Tie access revocation to HR events (role changes, terminations) so permissions don't outlive their justification.
4. **Use JIT and time-bound elevation** for administrative tasks instead of standing privileged access.
5. **Review service accounts as rigorously as human accounts.** They're often forgotten and disproportionately over-privileged.

## Visualizing the Impact

```
Standard Access:     [ User ] --> [ Only what's needed ] --> [ Limited blast radius ]
Excess Privilege:    [ User ] --> [ Broad, unused access ] --> [ Full network exposure ]
```

A simple before/after diagram like this — or a heat map showing "granted vs. actually used" permissions — makes for a compelling visual when publishing, and often surprises readers with just how wide that gap tends to be in practice.

## Closing Thoughts

Least Privilege isn't a one-time project — it's an ongoing discipline. Access naturally sprawls over time unless someone actively works against that drift. The organizations that get this right treat privilege management as a continuous process, not a checkbox from an audit two years ago.

Have you run into resistance implementing Least Privilege in your own organization? What tools or processes made the biggest difference? Share your experience in the comments — this is one of those principles that's easy to state and genuinely hard to live by.

**Next up in the series:** we move from limiting access to understanding the mind on the other side of the perimeter — how attackers actually think, plan, and operate.

---

*This is Part 1 of a 6-part series on Offensive vs Defensive Security.*
