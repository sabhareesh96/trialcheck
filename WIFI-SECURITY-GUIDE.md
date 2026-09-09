# Securing Wi-Fi with WPA + a 64-Character PSK — and How Attackers Try to Recover the Password

A defensive, threat-model guide. Goal: set up the strongest realistic home Wi-Fi
and understand *exactly* what you are defending against, so you can be confident
your password cannot be "reverse engineered" or cracked.

> Scope: this covers securing **your own** network and understanding the attacker's
> playbook conceptually so you can close every hole. It is not a tutorial for
> attacking networks you don't own.

---

## 1. What "WPA / WPS / 64 PSK" actually means

| Term | What it is | Security note |
|------|-----------|---------------|
| **WPA2-Personal (WPA2-PSK)** | Everyone shares one passphrase (the *Pre-Shared Key*). | Solid **only** if the passphrase is long and random. |
| **WPA3-Personal (SAE)** | Newer handshake ("Dragonfly"/SAE) that replaces the crackable PSK exchange. | **Best choice.** Resists offline password guessing even for shorter passwords. |
| **PSK** | The passphrase you type: **8–63 printable characters**. | It is stretched with PBKDF2(HMAC-SHA1, SSID, 4096 rounds) into a 256-bit key. |
| **"64 PSK"** | That 256-bit key written as **64 hexadecimal digits** — the raw key you can enter directly on many routers instead of a passphrase. | A full 64-hex key (or a 63-char random passphrase) is effectively **impossible to brute force**. |
| **WPS** | "Push-button / PIN" easy-setup feature. | **A major weakness — turn it OFF.** (See §3.) |

**Bottom line up front:** a *random* 63-character passphrase or a full 64-hex-digit PSK
defeats every password-guessing attack. But the key length only protects you if you
also **disable WPS**, because WPS bypasses the passphrase entirely.

---

## 2. How an attacker tries to "find" your Wi-Fi password

These are the real techniques, roughly in the order attackers try them. For each I list
**how it works** and **what stops it**.

### A. Capture the handshake, then crack it offline
The attacker sniffs the 4-way handshake that happens when a device joins (and can force
a rejoin by sending **deauth** frames). The handshake doesn't contain the password — it
contains a value *derived* from it. They then guess passwords **offline** at millions/sec
(tools: `aircrack-ng`, `hashcat`) until one reproduces the captured value.
- **Only works on weak/guessable passwords** (dictionary words, phone numbers, `Name+1234`).
- **Stopped by:** a long *random* PSK. A 63-char random / 64-hex key has too many
  combinations to ever guess. This is the single biggest reason to use a 64 PSK.

### B. The PMKID attack (no client needed)
A newer trick grabs a value called the **PMKID** directly from the router's first reply —
no connected victim required — then cracks it offline exactly like (A).
- **Stopped by:** the same long random PSK. (WPA3 also removes this exposure.)

### C. Attacking WPS instead of the password  ⚠️ *this bypasses your 64 PSK*
WPS PIN is an 8-digit setup code, but the protocol checks it in two halves and one digit
is a checksum, so the real guess-space collapses from 100,000,000 to about **11,000** —
crackable in hours (the *Reaver* attack). Worse, many chipsets leak enough that the PIN
can be computed **instantly** (the *Pixie-Dust* attack). Once the PIN is found, the router
**hands over your Wi-Fi password**, no matter how long it is.
- **Stopped by:** **disabling WPS completely** in the router admin page.

### D. Evil twin / rogue AP + fake "enter your Wi-Fi password" page
No cryptography broken at all. The attacker broadcasts a fake network with **your SSID**,
knocks your device off the real one, and shows a convincing "router update — please
re-enter your Wi-Fi password" captive page. The victim types the password in.
- **Stopped by:** using **WPA3**, enabling **802.11w / Protected Management Frames** (blocks
  the deauth kick), and simple awareness (a real router never asks for the Wi-Fi password
  in a web popup).

### E. Reverse-engineering the *default* key algorithm  ← the "reverse engineering" case
Many ISP/router vendors ship devices whose **default** Wi-Fi password is generated from the
**SSID or MAC address** by a fixed algorithm. Researchers reverse-engineer that algorithm
from the firmware; after that, the "secret" default password is simply *computed* from the
network name — no cracking needed. This is literally reverse engineering the password.
- **Stopped by:** **changing the default Wi-Fi password** to your own random one. Your custom
  64 PSK isn't derived from anything, so there is no algorithm to reverse.

### F. Reverse-engineering firmware / the companion phone app
The password (or an admin backdoor) may sit in the router's flash/NVRAM, in a companion
mobile app, or in a linked cloud account. Attackers dump firmware and hunt for hardcoded
credentials, backdoors, or the stored PSK.
- **Stopped by:** keeping **firmware updated**, setting a strong **router-admin** password,
  and turning off **remote/WAN administration**.

### G. Just reading it off a device that already knows it
If a laptop/phone/router the attacker can touch was ever connected, the saved password is
recoverable in plain text (Windows `netsh wlan show profile ... key=clear`, macOS Keychain,
the router's own admin page). This is often what "how he found the password" really means —
it was extracted from a trusted device, not cracked out of the air.
- **Stopped by:** device security (screen locks, disk encryption, a strong router-admin
  password) and not leaving the PSK saved on machines you don't control.

---

## 3. Your hardening checklist (do all of these)

1. **Use WPA3-Personal** if your router and devices support it; otherwise **WPA2-AES (CCMP)**.
   Turn **off** legacy **WPA/TKIP** and any "WPA/WPA2 mixed with TKIP" mode.
2. **Set a random PSK.** Either a **63-character random passphrase** or the full
   **64-hex-digit key**. Generate it randomly (password manager), don't invent it by hand.
   Example of the right *shape* (generate your own — never reuse a published one):
   `9f3c1ab7...` (64 hex chars) or a 63-char mix of letters/digits/symbols.
3. **Disable WPS** entirely (kills the Reaver / Pixie-Dust bypass in §2C).
4. **Enable 802.11w / Protected Management Frames** (blocks deauth → defeats the handshake-
   forcing and evil-twin kick in §2A/D). WPA3 makes this mandatory.
5. **Change the router-admin password** (separate from the Wi-Fi password) and **disable
   remote/WAN admin**.
6. **Update router firmware** and keep auto-updates on (closes §2F).
7. **Change any ISP default Wi-Fi name+password** so no default-key algorithm applies (§2E).
8. **Separate guest / IoT network** so a compromised gadget can't expose the main PSK.
9. *(Optional, strongest)* For business/home-lab: **WPA-Enterprise (802.1X/RADIUS)** — no
   shared password at all; every user/device authenticates individually.

---

## 4. Why the 64-character PSK is the core of this

- Attacks **A** and **B** are password **guessing** — a 64 PSK makes the number of guesses
  astronomically large, so they fail regardless of how much compute the attacker has.
- Attacks **C, D, E, F, G** do **not** guess the password — they **bypass** it (WPS),
  **trick** you into giving it up (evil twin), **compute** a default (algorithm), or **read**
  it from firmware/a device. The checklist in §3 is what closes those paths.

So: **a random 64 PSK + WPS disabled + WPA3/PMF + updated firmware + changed defaults** is a
setup where there is no realistic way for someone to "find" or reverse-engineer your password.
