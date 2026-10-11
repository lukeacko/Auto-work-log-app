# Security

This project includes an optional Firebase / Firestore version.

## Credentials

Do not commit Firebase service-account credentials or other secrets to this repository.

The expected local credential filename is:

```text
serviceAccount.json
```

That file is excluded by `.gitignore`.

If a real credential is ever committed accidentally, revoke or rotate it in Firebase immediately and remove it from the repository's Git history before making the repository public.
