---
id: TGT-ONEWEB-01
title: "OneWeb Platform Profile (Web.com & Newfold Digital)"
target: "Web.com Group / Newfold Digital"
platform: Bugcrowd
date: 2026-10-31
type: target_profile
status: Hunting
severity: None
cvss_score: null
bounty_payout: 0
vuln_class: "N/A"
root_cause_category: "N/A"
failure_reason: null
techniques:
  - asset-discovery
  - tech-stack-fingerprinting
  - api-surface-mapping
  - oauth-discovery
  - microfrontend-analysis
lessons_learned:
  - "OneWeb is a shared white-label platform across Web.com, Network Solutions, Bluehost, and HostGator."
  - "IdentityServer4 (ids4.builderservices.io) federates all microservice tokens and AI scopes."
---

# Target Profile: OneWeb Platform (Web.com Group / Newfold Digital)

## 1. Program Summary & Safe Harbor
- **Platform:** Bugcrowd
- **Target Organization:** Web.com Group / Newfold Digital
- **Architecture Core:** OneWeb White-label Microfrontend & BuilderServices API Cloud
- **Program Focus Areas:**
  1. `app.web.com` (Website builder feature & authenticated control panel)
  2. AI Features within (`gpt.newfold.com`, AI Image Generator, DALL-E, AI Domain Generator)
  3. Storefronts and Account Managers (Websites, servers, and APIs related to store/ecom management)
  4. Authenticated Subdomain Navigation Flows:
     - `app.web.com`
     - `www.networksolutions.com`
     - `https://www.bluehost.com/`
     - `https://www.hostgator.com/`

---

## 2. In-Scope Targets & Known Issue Baselines
| Target / Domain | Scope Role | Known Issues Baseline (Bugcrowd) |
| :--- | :--- | :--- |
| `app.web.com` | OneWeb Core App Shell / Builder | 3 known issues |
| `www.networksolutions.com` | Sister Brand Portal | 135 known issues (Cloudflare, jQuery) |
| `https://www.bluehost.com/` | Hosting Brand Portal | 15 known issues |
| `https://www.hostgator.com/` | Hosting Brand Portal | 9 known issues |

---

## 3. Discovered Infrastructure & Architecture Blueprint

### 3.1 Client-Side Shell (Microfrontends)
- **Deployment Endpoint:** Azure Blob Storage (`frontendprod.blob.core.windows.net/frontend-deployments/3543/universal/app-shell/default/index.html`)
- **Loader:** SystemJS 6.1.1 (`import-map.json`)
- **Key Modules Identified:**
  - `app-ai` (`/ai/174/main.bundle.js`): General AI generation features
  - `app-ai-dalle-generator` (`/aiimagegenerator/49/main.bundle.js`): DALL-E image generation
  - `app-public-domain-generator` (`/aidomaingenerator/1445/main.bundle.js`): AI Domain Generator
  - `app-account-settings` (`/account/2556/main.bundle.js`): Account management
  - `app-control-panel-store` (`/store/368/main.bundle.js`): Storefront configuration
  - `app-storedash-*` (orders, products, settings, checkout, integrations, warehouses)

### 3.2 Central Identity & Auth Federation (IdentityServer4)
- **Discovery Endpoint:** `https://ids4.builderservices.io/.well-known/openid-configuration`
- **Identity Provider:** IdentityServer4 on .NET 9.0 (`ID_NET9_0`)
- **Auth Endpoint:** `https://ids4.builderservices.io/connect/authorize`
- **Token Endpoint:** `https://ids4.builderservices.io/connect/token`
- **Supported AI & Internal Scopes:**
  `ai-api`, `nf-ai-api`, `accounts-api`, `sites-api`, `skoruba_identity_admin_api`, `cst_api`, `provisioning-api`, `business-profile-api`, `omni-api`, `translations-management-api`
- **Supported Tokens & Claims:**
  `partner_id`, `account_id`, `user_id`, `crm_account_id`, `crm_user_id`, `role`, `roles`, `agent_email`, `agent_name`

### 3.3 Backend API Mesh
- **AI Gateway:** `https://gpt.newfold.com` -> `https://api-gw.builderservices.io/nf-ai-api/NewfoldGpt`
- **Central API Hub:** `https://next-apis-prod.builderservices.io/`
  - `/storedash-accounts-api`
  - `/storedash-orders-api`
  - `/storedash-products-api`
  - `/storedash-payments-api`
  - `/storedash-settings-api`
  - `/billing-api`
  - `/contacts-api`
- **App Gateways:**
  - `https://app-gateway.web.com`
  - `https://app-gateway.networksolutions.com`
  - `https://app-gateway.register.com`
- **CSRF Token Flow:** Pre-auth endpoint `/v1.0/session/preauth` returning header `X-CSRF-TOKEN`

---

## 4. High-Yield Attack Hypotheses (For Collaborative Testing)

### Hypothesis 1: Multi-Tenant / Cross-Brand Partner ID Tampering (BOLA/IDOR)
- **Context:** `_partnerId: 158` (Web.com) vs `_partnerId: 157` (Network Solutions).
- **Mechanism:** Both properties talk to the exact same backend endpoints on `builderservices.io`. If requests accept `partner_id`, `account_id`, or `siteId` in JSON bodies or query strings, does the server enforce that the caller's JWT token matches the `partner_id` and tenant organization?

### Hypothesis 2: AI Feature Prompt Injection & Server-Side Sink Abuse (SSRF / Data Leakage)
- **Context:** The AI modules (`app-ai`, `app-ai-dalle-generator`, `app-public-domain-generator`) call `https://api-gw.builderservices.io/nf-ai-api/NewfoldGpt`.
- **Mechanism:**
  - Can system prompt extraction reveal internal system instructions, API keys, or database endpoints?
  - When the AI generates website content, templates, or logo images, does it accept image URLs or external references that trigger server-side fetching (SSRF) via `images.builderservices.io/s/?`?

### Hypothesis 3: Storefront & E-commerce Checkout Logic (Price Tampering & Race Conditions)
- **Context:** Ecomdash and StoreDash handle inventory, orders, and payment integrations (`/storedash-orders-api`, `/storedash-payments-api`).
- **Mechanism:**
  - Currency conversion desync or negative unit quantities in order creation.
  - Coupon / voucher race conditions during multi-threaded checkout requests (CWE-362).

### Hypothesis 4: IdentityServer4 OAuth Token & Scope Escalation
- **Context:** The discovery doc lists high-privilege scopes: `skoruba_identity_admin_api`, `cst_api` (Customer Support Tool), `admin-panel-panel-api`.
- **Mechanism:**
  - Does the authorization endpoint allow requesting extra scopes during OAuth authorization code flow?
  - PKCE downgrade: Does the token endpoint accept `code_challenge_method=plain` when the authorization code was issued?
