# Intune export scope

This document defines the canonical Intune entities we export, along with a shared schema for the exported asset payloads and their assignments.

## Export scope (by asset type)

| Asset type key | User-friendly label | Microsoft Graph resource name | Collection path |
| --- | --- | --- | --- |
| deviceConfigurations | Device configurations | `deviceConfiguration` | `/deviceManagement/deviceConfigurations` |
| deviceCompliancePolicies | Device compliance policies | `deviceCompliancePolicy` | `/deviceManagement/deviceCompliancePolicies` |
| configurationPolicies | Settings catalog policies | `deviceManagementConfigurationPolicy` | `/deviceManagement/configurationPolicies` |
| groupPolicyConfigurations | Administrative templates (ADMX) | `groupPolicyConfiguration` | `/deviceManagement/groupPolicyConfigurations` |
| deviceManagementIntents | Security baselines | `deviceManagementIntent` | `/deviceManagement/intents` |
| deviceHealthScripts | Proactive remediation scripts | `deviceHealthScript` | `/deviceManagement/deviceHealthScripts` |
| deviceManagementScripts | PowerShell scripts (Windows) | `deviceManagementScript` | `/deviceManagement/deviceManagementScripts` |
| deviceShellScripts | Shell scripts (macOS) | `deviceShellScript` | `/deviceManagement/deviceShellScripts` |
| mobileApps | Mobile apps | `mobileApp` | `/deviceAppManagement/mobileApps` |
| mobileAppConfigurations | App configuration policies | `mobileAppConfiguration` | `/deviceAppManagement/mobileAppConfigurations` |
| managedAppProtections | App protection policies | `managedAppProtection` (android/ios/windows variants) | `/deviceAppManagement/managedAppPolicies` |
| targetedManagedAppConfigurations | Targeted app configuration policies | `targetedManagedAppConfiguration` | `/deviceAppManagement/targetedManagedAppConfigurations` |
| windowsAutopilotDeploymentProfiles | Windows Autopilot deployment profiles | `windowsAutopilotDeploymentProfile` | `/deviceManagement/windowsAutopilotDeploymentProfiles` |
| enrollmentConfigurations | Device enrollment configurations | `deviceEnrollmentConfiguration` | `/deviceManagement/deviceEnrollmentConfigurations` |
| windowsFeatureUpdateProfiles | Windows feature update profiles | `windowsFeatureUpdateProfile` | `/deviceManagement/windowsFeatureUpdateProfiles` |
| windowsQualityUpdateProfiles | Windows quality update profiles | `windowsQualityUpdateProfile` | `/deviceManagement/windowsQualityUpdateProfiles` |
| windowsDriverUpdateProfiles | Windows driver update profiles | `windowsDriverUpdateProfile` | `/deviceManagement/windowsDriverUpdateProfiles` |
| notificationMessageTemplates | Company portal notification templates | `notificationMessageTemplate` | `/deviceManagement/notificationMessageTemplates` |
| termsAndConditions | Terms and conditions | `termsAndConditions` | `/deviceManagement/termsAndConditions` |
| assignmentFilters | Assignment filters | `assignmentFilter` | `/deviceManagement/assignmentFilters` |

## Exported asset schema (shared)

Every exported entity is normalized into a single "exported asset" shape.

```json
{
  "id": "string",
  "displayName": "string",
  "type": "string",
  "settings": {},
  "assignments": [],
  "sourceResource": {
    "graphResourceName": "string",
    "graphCollectionPath": "string"
  },
  "raw": {}
}
```

### Field definitions

- `id`: The Graph object ID.
- `displayName`: The human-readable name for the asset.
- `type`: One of the asset type keys listed in the export scope table.
- `settings`: Normalized, product-ready representation of the asset's meaningful settings.
- `assignments`: An array of assignment objects (see below).
- `sourceResource`: Metadata about the Graph resource used to fetch the item.
- `raw`: The raw Graph response for audit/debugging.

### Assignments model

Assignments connect the exported asset to AAD groups and capture scope/intent.

```json
{
  "target": {
    "groupId": "string",
    "groupDisplayName": "string",
    "groupType": "security | microsoft365 | dynamic",
    "assignmentType": "include | exclude"
  },
  "intent": "required | available | uninstall | notApplicable",
  "delivery": {
    "notification": "showAll | showReboot | hideAll",
    "restartSettings": "string"
  },
  "schedule": {
    "startDateTime": "2024-01-01T00:00:00Z",
    "endDateTime": null
  }
}
```

Notes:
- `intent` values vary by asset type (for example, app intent vs. update policy intent). Use the closest native Graph value where applicable.
- `delivery` and `schedule` are optional and can be omitted when not available on the source resource.
