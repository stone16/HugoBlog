# stometa.dev

The personal publishing platform of Leilei Chen (Stometa): a bilingual technical
blog, its reader conversation, and a self-hosted way to hand a locally-built
page or document to a specific audience.

## Language

### Publishing

**Post**:
A piece of writing authored in exactly one language and published on the blog.
_Avoid_: Article, entry, note

**Locale**:
The single language a Post is written in — `zh` or `en`. A Post always has one
and never has two.
_Avoid_: Language, lang, i18n

**Translation Group**:
The link between two Posts that say the same thing in different Locales. Most
Posts belong to no Translation Group; only deliberately translated pairs do.
_Avoid_: Translation, i18n group, post pair

**Revision**:
A previous state of a Post, retained so that any change — including one made
autonomously by Nexus — can be inspected and undone.
_Avoid_: Version, history, draft

**Nexus**:
The external agent pipeline (ContentGenerator) that authors and publishes Posts
without a human at the keyboard. It is a peer of the Admin, not a subordinate
of it.
_Avoid_: The bot, the generator, the publisher

### Conversation

**Comment**:
A reader's public response attached to a Post.
_Avoid_: Reply, feedback, discussion

**Commenter**:
The identity behind a Comment — a self-declared display name, with no account
behind it.
_Avoid_: User, reader, author (author means Stometa)

**Trusted Commenter**:
A Commenter whose first Comment was approved, and whose later Comments publish
without waiting.
_Avoid_: Verified user, whitelisted user

**Moderation Queue**:
The set of Comments awaiting a decision before they become visible.
_Avoid_: Inbox, pending list

### Sharing

**Artifact**:
A self-contained HTML page or PDF built locally and published to its own
address so specific people can open it. It is not a Post: it has no feed, no
Locale, and no Comments.
_Avoid_: Share, upload, page, document

**Slug**:
The subdomain label that addresses an Artifact — the `topic1` in
`topic1.stometa.dev`. Chosen at publish time, unique forever.
_Avoid_: ID, name, key

**Update Key**:
The secret that proves the right to replace or withdraw an already-published
Artifact.
_Avoid_: Token, password, api key

**Admin**:
Stometa, acting through the authenticated management interface — the only
identity that may write Posts by hand, decide Comments, or publish Artifacts.
_Avoid_: Owner, superuser, root
