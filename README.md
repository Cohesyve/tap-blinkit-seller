# Tap-Blinkitseller

## Usage

```bash
tap_blinkit_seller --config config.json --discover > catalog.json
singer-discover --input catalog.json --output catalog-selected.json
tap_blinkit_seller --config config.json --catalog catalog-selected.json > data.txt
```
