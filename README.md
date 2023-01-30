# api_to_onedrive

This script traverses user-defined routes on an API, flattens the response into a CSV, and then uploads that CSV to Microsoft OneDrive.

## Getting started

1. Under 'App Registrations' register a new App
2. Copy the application (client) ID somewhere
3. Within the App, under `Certificates & secrets`, create a new client secret - STORE THIS SAFELY
4. Within the App, under `API permissions`, add the following permissions:
Microsoft Graph > Application Permissions
- Files.ReadWrite.All
- Sites.ReadWrite.All

clone out the .env-template and enter your details
install the requirements dependencies
run the script