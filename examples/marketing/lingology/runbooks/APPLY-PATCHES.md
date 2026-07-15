# Runbook: zastosuj integracje Scrapling na swoich forkach

Bot Cursora **nie może** pushować do `openshorts` / `marketingskills` / `ai-website-cloner-template` (403). Patche są w tym repo.

## 0. Pobierz Scrapling z tym PR

```bash
mkdir -p ~/projekty && cd ~/projekty
git clone https://github.com/talkshiftkontakt-spec/Scrapling.git
cd Scrapling
git fetch origin
git checkout cursor/olx-iphone-scraper-f0cc

export SCRAPLING_INTEGRATIONS="$PWD/examples/integrations"
```

## 1. OpenShorts

```bash
cd ~/projekty
git clone https://github.com/talkshiftkontakt-spec/openshorts.git
cd openshorts
git checkout -b cursor/scrapling-integration-f0cc
git am "$SCRAPLING_INTEGRATIONS/openshorts/patches/"*.patch
git push -u origin cursor/scrapling-integration-f0cc
```

Test:

```bash
pip install "scrapling[fetchers]>=0.4.10"
python scripts/test_scrapling_scrape.py https://www.lingology.pl
python scripts/test_scrapling_scrape.py https://www.lingotutor.pl/welcome
```

## 2. marketingskills

```bash
cd ~/projekty
git clone https://github.com/talkshiftkontakt-spec/marketingskills.git
cd marketingskills
git checkout -b cursor/scrapling-integration-f0cc
git am "$SCRAPLING_INTEGRATIONS/marketingskills/patches/"*.patch
git push -u origin cursor/scrapling-integration-f0cc
```

Test (opcjonalnie — raw scrapes masz już w `examples/marketing/lingology/scrapes/`):

```bash
python scripts/scrape-competitor-scrapling.py \
  --slug preply --url https://preply.com/pl/ --pages /
```

## 3. ai-website-cloner

```bash
cd ~/projekty
git clone https://github.com/talkshiftkontakt-spec/ai-website-cloner-template.git
cd ai-website-cloner-template
git checkout -b cursor/scrapling-integration-f0cc
git am "$SCRAPLING_INTEGRATIONS/ai-website-cloner/patches/"*.patch
git push -u origin cursor/scrapling-integration-f0cc
```

Test:

```bash
python scripts/scrapling-preflight.py https://www.lingology.pl
python scripts/scrapling-preflight.py https://www.lingotutor.pl/welcome
```

## Konflikt przy `git am`

```bash
git am --abort
# skopiuj pliki ręcznie z examples/integrations/<projekt>/
```
