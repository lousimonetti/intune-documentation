# intune-documentation

Generate Intune documentation exports in multiple formats for different audiences.

## Usage

```bash
intune-doc export --format word --audience client --scope full_settings --output ./reports/intune
```

You can repeat `--format` or provide a comma-separated list:

```bash
intune-doc export --format word,excel,pdf,ppt --audience admin --scope assignment_summary --output ./reports/intune
```
