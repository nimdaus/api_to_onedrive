# api_to_onedrive

This script traverses user-defined routes on an API, flattens the response into a CSV, and then uploads that CSV to Microsoft OneDrive.

## Getting started

### Under 'App Registrations' register a new App
### Copy the application (client) ID somewhere
### Within the App, under `Certificates & secrets`, create a new client secret - STORE THIS SAFELY
### Within the App, under `API permissions`, add the following permissions:
Microsoft Graph > Application Permissions
- Files.ReadWrite.All
- Sites.ReadWrite.All

clone out the .env-template and enter your details
install the requirements dependencies
run the script