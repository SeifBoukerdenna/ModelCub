# Philosophy

ModelCub is built on core principles that guide every decision we make.

<div class="philosophy-grid">

## 🔒 Privacy-First

**Your data never leaves your machine.**

No telemetry. No tracking. No "anonymous" analytics. No exceptions.

When you train a model with ModelCub, every byte stays on your infrastructure. We built this for medical imaging teams, pharmaceutical companies, and anyone who can't or won't put their data in someone else's cloud.

Privacy isn't a feature. It's the foundation.

---

## 🎯 Simple by Default

**Complexity is optional.**

One command to fix datasets. One command to train. Default settings that work.

We don't hide complexity—we make it optional. Auto mode gets you started instantly. Manual mode gives you full control when you need it.

The best tool is the one that gets out of your way.

---

## 💰 Zero Lock-In

**You can leave anytime.**

Open source (MIT license). Self-hosted. Export to any format. Your data, your models, your infrastructure.

Cloud platforms trap you with proprietary formats and migration costs. We do the opposite: make it trivial to leave. Export to ONNX, TensorRT, or whatever you need.

Confidence comes from knowing you're never trapped.

---

## 🛠️ Developer-Focused

**Built by developers, for developers.**

Clean APIs. Clear documentation. No marketing fluff. No "enterprise" paywalls.

We're developers who built what we needed. Command-line tools that compose. Python SDK that feels natural. Error messages that help instead of confuse.

The best users are the ones who read your code.

---

## 📚 Reproducible

**Science requires reproducibility.**

Version datasets like git. Commit, diff, rollback. Full audit trail for every training run.

Academic papers need reproducible experiments. Regulated industries need compliance trails. Production systems need to know exactly what changed.

Reproducibility isn't optional—it's engineering.

---

## 🌍 Community-Driven

**We listen. We iterate. We ship.**

Open roadmap. Public discussions. Fast responses to issues.

The best features come from users. We're building this with the community, not for theoretical users. Every release reflects real feedback from real workflows.

Good software comes from listening.

</div>

---

## In Practice

These aren't just words. Here's what they mean:

**Privacy-First**: No `pip install` phones home. No update checks. No usage stats.

**Simple by Default**: `modelcub train --dataset bears --auto` just works.

**Zero Lock-In**: `modelcub export --format onnx` exports to any platform.

**Developer-Focused**: Error says "corrupt image at line 45" not "something went wrong."

**Reproducible**: `modelcub diff v1 v2` shows exactly what changed.

**Community-Driven**: GitHub issue filed Monday, fix shipped Thursday.

## Join the Movement

ModelCub represents a different way of building ML tools:
- Local-first, not cloud-first
- Privacy-first, not data-first
- Users-first, not revenue-first

If you believe in these principles, **[we want your help](https://github.com/SeifBoukerdenna/ModelCub/blob/main/CONTRIBUTING.md)**.

<style scoped>
.philosophy-grid {
  margin: 48px 0;
}

.philosophy-grid h2 {
  font-size: 1.75rem;
  margin-top: 48px;
  margin-bottom: 16px;
  padding-top: 0;
  border-top: none;
}

.philosophy-grid h2:first-of-type {
  margin-top: 0;
}

.philosophy-grid p strong {
  color: var(--vp-c-brand-1);
  font-weight: 600;
  font-size: 1.1rem;
}

.philosophy-grid hr {
  margin: 48px 0;
  border: none;
  border-top: 1px solid var(--vp-c-divider);
}

h2 {
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid var(--vp-c-divider);
}

ul {
  margin-top: 16px;
}

li {
  margin-bottom: 8px;
}
</style>