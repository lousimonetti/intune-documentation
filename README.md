# intune-documentation

Generate Intune documentation exports in multiple formats for different audiences using either
Python or PowerShell.

## Usage

```bash
intune-doc export --format word --audience client --scope full_settings --output ./reports/intune
```

You can repeat `--format` or provide a comma-separated list:

```bash
intune-doc export --format word,excel,pdf,ppt --audience admin --scope assignment_summary --output ./reports/intune
```

## Prerequisites

### Python

- Python 3.11+
- An Entra ID app registration with Microsoft Graph permissions for Intune exports
- `config.yaml` created from the provided `config.example.yaml`

### PowerShell

- PowerShell 7+
- Microsoft Graph PowerShell SDK installed
- An Entra ID app registration with Microsoft Graph permissions for Intune exports
- `config.yaml` created from the provided `config.example.yaml`

## Configuration

1. Copy the example configuration file:

   ```bash
   cp config.example.yaml config.yaml
   ```

2. Update the following values in `config.yaml`:
   - `tenant_id`
   - `client_id`
   - `client_secret` (leave blank if using device code)
   - `use_device_code`
   - `output_directory`
   - `report_options`

## Running (Python)

```bash
python -m intune_doc export --format word --audience client --scope full_settings --output ./reports/intune
```

```bash
python -m intune_doc export --format word,excel,pdf,ppt --audience admin --scope assignment_summary --output ./reports/intune
```

## Running (PowerShell)

```powershell
pwsh ./scripts/Export-IntuneDocumentation.ps1 -ConfigPath ./config.yaml -Format Word -Audience Client -Scope FullSettings -OutputPath ./reports/intune
```

```powershell
pwsh ./scripts/Export-IntuneDocumentation.ps1 -ConfigPath ./config.yaml -Format Word,Excel,Pdf,Ppt -Audience Admin -Scope AssignmentSummary -OutputPath ./reports/intune
```

## Tests

Run the unit tests with the standard library test runner:

```bash
python -m unittest discover -s tests
```

Run an individual test module:

```bash
python -m unittest tests.test_cli
```
