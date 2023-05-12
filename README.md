# Game Update Notifier

A bot that will let you know via Discord as soon as a new version of your favorite game on Steam, Epic Games, Microsoft Store, and GOG are released.

This bot tracks actual package updates, instead of updates of any news feeds like blog posts or release notes, so you can be the first to know the release of the new patches.

![Sample message for updates on Steam](https://user-images.githubusercontent.com/2920259/120804770-ff51c700-c57f-11eb-8c0d-79f821266bf3.png)
![Sample message for updates on Epic Games](https://user-images.githubusercontent.com/2920259/120804784-01b42100-c580-11eb-80b4-a62cf65b370a.png)
![Sample message for updates on Microsoft Store](https://user-images.githubusercontent.com/2920259/120804776-011b8a80-c580-11eb-8d45-28e7efa94dd7.png)

## Table of Contents

- [Game Update Notifier](#game-update-notifier)
  - [Table of Contents](#table-of-contents)
  - [Supported Platforms](#supported-platforms)
    - [Targets to Track](#targets-to-track)
    - [Notification Destination](#notification-destination)
  - [Installation](#installation)
    - [Requirements](#requirements)
    - [Prepare your Discord](#prepare-your-discord)
    - [Prepare Game Update Notifier](#prepare-game-update-notifier)
    - [Prepare Application IDs to track](#prepare-application-ids-to-track)
      - [Steam](#steam)
      - [Epic Games](#epic-games)
      - [Microsoft Store](#microsoft-store)
      - [GOG](#gog)
    - [Prepare Environment Variables (`.env`)](#prepare-environment-variables-env)
    - [Run the Bot](#run-the-bot)
  - [Data Persistence](#data-persistence)
  - [Related Projects](#related-projects)

## Supported Platforms

### Targets to Track

| Platform          | Auth           | Products                     |
| ----------------- | -------------- | ---------------------------- |
| ✅ Steam           | ✅ Not required | ✅ Unrestricted               |
| ✅ Microsoft Store | ✅ Not required | ✅ Unrestricted               |
| ✅ Epic Games      | ⚠️ Required     | ⚠️ Only products that you own |
| ✅ GOG             | ✅ Not required | ✅ Unrestricted               |

### Notification Destination

| Platform  | Target         | Method    |
| --------- | -------------- | --------- |
| ✅ Discord | ✅ Users, Roles | ✅ Webhook |

## Installation

### Requirements

- Docker (Or Podman)
- Docker Compose

### Prepare your Discord

1. Get **Webhook URL** for the Channel in your Guild that the notification message to be posted.
2. (If required) Get **User IDs** to be mentioned in the notification message.
3. (If required) Get **Role IDs** to be mentioned in the notification message.

### Prepare Game Update Notifier

CLone this repository or download `docker-compose.yml` and `sample.env`, then rename `sample.env` as `.env`.

### Prepare Application IDs to track

Prepare Product IDs on each platform that you want to track.

#### Steam

Get **Application ID** from the URL of [the store page](https://store.steampowered.com/) for each product.

- For example, the URL of **Outer Wilds** is `https://store.steampowered.com/app/753640/Outer_Wilds/`
- The Application ID that can be found in the URL is `753640`

For bundle SKU that include multiple products, obtain the ID of the actual product included in the bundle (i.e. **Among Us** (`945360`) instead of **Among Us Starter Pack** (`16867`)).

Get **Branch Name** of the product to track. You can use the helper script in this repository to gather branch name for each product. Usualy `public` is the best branch to track.

```bash
$ docker compose run --rm notifier helper/app_finder.py -p steam -i 753640
KEY               App Id  Name         Branch      Updated Time
--------------  --------  -----------  --------  --------------
753640:public     753640  Outer Wilds  public        1595281461
753640:neowise    753640  Outer Wilds  neowise       1603749868
753640:staging    753640  Outer Wilds  staging       1594088316
```

Keep the value of the `KEY` column (`<App Id>:<Branch>`) of the row of the branch you want to track. This value can be used to prepare `.env` file in later steps.

#### Epic Games

Get **Application ID** by using the helper script in this repository.

First, run the following command and open the indicated URL in your browser. Once authenticated, keep the `sid` displayed and enter the `sid` to the prompt.

```bash
$ docker compose run --rm notifier helper/epicgames_auth.py
[cli] INFO: Testing existing login data if present...
Please login via the epic web login!
If web page did not open automatically, please manually open the following URL: https://www.epicgames.com/id/login?redirectUrl=https://www.epicgames.com/id/api/redirect
Please enter the "sid" value from the JSON response: 14b8c***********************8fb5
[cli] INFO: Successfully logged in as "<Your Account>"
```

Then run the following command to get the list of the products that you own.

```bash
$ docker compose run --rm notifier helper/app_finder.py -p epicgames
[Core] INFO: Trying to re-use existing login session...
KEY                               App Id                            Name                         Build Version
--------------------------------  --------------------------------  ---------------------------  ------------------
963137e4c29d4c79a81323b8fab03a40  963137e4c29d4c79a81323b8fab03a40  Among Us                     2021.5.25.2
bcbc03d8812a44c18f41cf7d5f849265  bcbc03d8812a44c18f41cf7d5f849265  Cities: Skylines             1.13.3-f9
Kinglet                           Kinglet                           Sid Meier's Civilization VI  1.0.12.564030h_rtm
```

Keep the value of the `KEY` column (equals to `App Id`) of the product you want to track. This value can be used to prepare `.env` file in later steps.

#### Microsoft Store

Get **Application ID** from the URL of [the store page](https://www.microsoft.com/en-us/store/games/windows) for each product.

- For example, the URL of **Minecraft for Windows 10** is `https://www.microsoft.com/en-us/p/minecraft-for-windows-10/9nblggh2jhxj`
- The Product ID that can be found in the URL is `9nblggh2jhxj`

For bundle SKU that include multiple products, obtain the ID of the actual product included in the bundle (i.e. **Minecraft for Windows 10** (`9nblggh2jhxj`) instead of **Minecraft for Windows 10 Starter Collection** (`9n4km90ctzt6`)).

Get **Platform Name** of the product to track. You can use the helper script in this repository to gather platform name for each product. Usualy `Windows.Desktop` or `Windows.Universal` is the best platform to track.

```bash
$ docker compose run --rm notifier helper/app_finder.py -p msstore -m JP -i 9nblggh2jhxj
KEY                             App Id        Market    Name                      Platform           Package Id
------------------------------  ------------  --------  ------------------------  -----------------  ----------------------------------------
9nblggh2jhxj:Windows.Xbox       9nblggh2jhxj  JP        Minecraft for Windows 10  Windows.Xbox       845277e2-565d-741e-3c91-a883a873d4be-Arm
9nblggh2jhxj:Windows.Universal  9nblggh2jhxj  JP        Minecraft for Windows 10  Windows.Universal  6c489be8-f48d-a78b-a405-44633558c5f7-Arm
9nblggh2jhxj:Windows.Xbox       9nblggh2jhxj  JP        Minecraft for Windows 10  Windows.Xbox       426ccf1b-9364-fc9a-3a9d-f24ab7b493a6-X86
9nblggh2jhxj:Windows.Universal  9nblggh2jhxj  JP        Minecraft for Windows 10  Windows.Universal  7ac62c84-44fc-8c53-3f64-549fcbe9c471-X86
9nblggh2jhxj:Windows.Universal  9nblggh2jhxj  JP        Minecraft for Windows 10  Windows.Universal  78c121c0-7dc6-29ca-7a71-3298afb37686-X64
9nblggh2jhxj:Windows.Xbox       9nblggh2jhxj  JP        Minecraft for Windows 10  Windows.Xbox       b0d37c82-091c-c4c5-e702-d7e12aff541d-X64
```

Keep the value of the `KEY` column (`<App Id>:<Platform>`) of the row of the platform you want to track. This value can be used to prepare `.env` file in later steps.

#### GOG

Both the **App ID** and **Branch** can be found by searching via product name using the helper script in this repository. The main release branch is usually `null`.

```bash
$ docker compose run --rm notifier helper/app_finder.py -p gog -n Kenshi
KEY                                                      App Id  Name        Branch
---------------------------------------------------  ----------  ----------  ----------------------------------------
1193046833:"experimental - latest unstable version"  1193046833  Kenshi      "experimental - latest unstable version"
1193046833:null                                      1193046833  Kenshi      null
1409800471:null                                      1409800471  Mahokenshi  null
```

Keep the value of the `KEY` column (`<App Id>:<Branch>`) of the row of the branch you want to track. This value can be used to prepare `.env` file in later steps.

### Prepare Environment Variables (`.env`)

Copy `sample.env` as `.env` and fill in the each lines to suit your requirements. Follow the instructions in the `.env` file.

### Run the Bot

If you want to track the products on Epic Games, first store the credential in the volume.

Run the following command and open the indicated URL in your browser. Once authenticated, keep the `sid` displayed and enter the `sid` to the prompt.

```bash
$ docker compose run --rm notifier helper/epicgames_auth.py
[cli] INFO: Testing existing login data if present...
Please login via the epic web login!
If web page did not open automatically, please manually open the following URL: https://www.epicgames.com/id/login?redirectUrl=https://www.epicgames.com/id/api/redirect
Please enter the "sid" value from the JSON response: 14b8c***********************8fb5
[cli] INFO: Successfully logged in as "<Your Account>"
```

Once everything goes good, simply start the Bot by following command.

```bash
docker compose up -d
```

## Data Persistence

- `/app/cache`, `./cache`
  - Used to cache gathered data.
- `/app/.config`, `~/.config`
  - Used to store credential for Epic Games.

## Related Projects

- [lovvskillz/python-discord-webhook](https://github.com/lovvskillz/python-discord-webhook)
- [ValvePython/steam](https://github.com/ValvePython/steam)
- [derrod/legendary](https://github.com/derrod/legendary)
