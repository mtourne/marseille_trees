
## Pre-requisites
- Google Maps API key(s) with "Street View Static API" enabled
  - To create a billing account and enable the Street View API, please refer to the official guide [here](https://developers.google.com/maps/gmp-get-started)
  - To issue API keys, read [here](https://developers.google.com/maps/documentation/streetview/get-api-key)
  - **IMPORTANT**: As API requests are billed beyond the free credit of $200 per month (per billing account), please be careful with your API keys. To find out more, refer to the section ["Using the Google Maps API"](#using-the-google-maps-api).


## Basics - Monitoring API usage / Managing API keys
As of April 2020, each Static Street View request (except for metadata) costs [0.007 USD per request](https://developers.google.com/maps/documentation/streetview/usage-and-billing#static-street-view), 
Therefore, the $200 free credit per month translates to 28,571 requests you can make for free, per billing account.
You can keep track of your API usage in near-realtime (it may take ~5 minutes for usage to update) as follows:

1. Go to the [Google Cloud Platform console](https://console.cloud.google.com/).
2. Navigate to APIs & Services > Credentials.
3. You will see a list of API keys that have been generated. Using the console, you can monitor usage per API key and delete API keys as necessary.

# Disabling billing to stop usage beyond free credit

After setting budgets and alerts, we can take a further step to disable billing once it goes over the free credit amount. Please note that once billing is stopped, you would have to re-enable billing on your project to continue using the API keys in the future (say, next month).

## Step 1. Setting budgets and budget alerts
1. Go to the [Google Cloud Platform console](https://console.cloud.google.com/).
2. Click on the sidebar icon and navigate to Billing > Budgets & alerts. 
3. Click on "Create Budget".
4. Enter `name`, `projects` and `products` as appropriate. For example, if you opened an account solely for the purpose of running Treepedia, you may want to follow the settings below.
    - Name: street-view-api-budget
    - Project: (Select the project for which you have created the Street View Static API key)
    - Product: Street View Static API
5. Click "Next".
6. Set amount as follows.
    - Budget type: "Specified amount"
    - Target amount*: USD190 (or the equivalent in your local currency e.g. 20000JPY)
    - Make sure "Include credits in cost" is **unchecked**.
7. Under "Manage notifications", check "Connect a Pub/Sub topic to this budget.
    - Project: (Select the project for which you have created the Street View Static API key)
    - Select a Cloud Pub/Sub topic: Click and select "Create a topic". Set Topic ID to `stop-billing` and click "Create topic".
8. Click "Save".

*Note: As there is latency between incurring costs and receiving budget notifications, it is advisable to set the target amount to an amount slightly lower than the free credit amount (i.e. USD200).

You will receive email notifications when 50%, 90%, and 100% of your budget has been exceeded. (You can customise the thresholds.) This will keep you informed of your API usage and any suspicious activity (e.g. leakage of API key).

For details please check out the [official documentation](https://cloud.google.com/billing/docs/how-to/budgets).

## Step 2. Create a Cloud Function
1. Navigate to Cloud Functions.
2. Click "Create function".
3. Change Name to `stop-billing`.
4. Under Trigger, select Cloud Pub/Sub and select the topic you have created in Step 1-7.
5. Under Source Code, go to the `package.json` tab and paste in the follows.
```
{
 "name": "cloud-functions-billing",
 "version": "0.0.1",
 "dependencies": {
    "google-auth-library": "^2.0.0",
    "googleapis": "^33.0.0"
 }
}
```
6. Switch to the `Index.js` tab and paste in the follows.
```
const {google} = require('googleapis');
const {auth} = require('google-auth-library');

const PROJECT_ID = process.env.GCP_PROJECT;
const PROJECT_NAME = `projects/${PROJECT_ID}`;
const billing = google.cloudbilling('v1').projects;

exports.stopBilling = async (pubsubEvent, context) => {
  const pubsubData = JSON.parse(
    Buffer.from(pubsubEvent.data, 'base64').toString()
  );
  if (pubsubData.costAmount <= pubsubData.budgetAmount) {
    return `No action necessary. (Current cost: ${pubsubData.costAmount})`;
  }

  await _setAuthCredential();
  if (await _isBillingEnabled(PROJECT_NAME)) {
    return _disableBillingForProject(PROJECT_NAME);
  } else {
    return 'Billing already disabled';
  }
};

/**
 * @return {Promise} Credentials set globally
 */
const _setAuthCredential = async () => {
  const res = await auth.getApplicationDefault();

  let client = res.credential;
  if (client.hasScopes && !client.hasScopes()) {
    client = client.createScoped([
      'https://www.googleapis.com/auth/cloud-billing',
      'https://www.googleapis.com/auth/cloud-platform',
    ]);
  }

  // Set credential globally for all requests
  google.options({
    auth: client,
  });
};

/**
 * Determine whether billing is enabled for a project
 * @param {string} projectName Name of project to check if billing is enabled
 * @return {bool} Whether project has billing enabled or not
 */
const _isBillingEnabled = async (projectName) => {
  const res = await billing.getBillingInfo({name: projectName});
  return res.data.billingEnabled;
};

/**
 * Disable billing for a project by removing its billing account
 * @param {string} projectName Name of project disable billing on
 * @return {string} Text containing response from disabling billing
 */
const _disableBillingForProject = async (projectName) => {
  const res = await billing.updateBillingInfo({
    name: projectName,
    resource: {billingAccountName: ''}, // Disable billing
  });
  return `Billing disabled: ${JSON.stringify(res.data)}`;
};
```
 
7. Change Function to execute to `stopBilling`.
8. Click "Create".
9. As your cloud function is being created, click on it to view details.
10. Note the email address under Service Account. It should look something like `project-name@appspot.gserviceaccount.com`.

## Step 3: Granting billing permissions to Service Account
1. On Cloud console, go to Billing > Account Management.
2. Under Permissions panel, click Add members. If Permissions panel is not shown, click "Show info panel" on the page.
3. In the New Members field, enter the email address you have noted (e.g. `project-name@appspot.gserviceaccount.com`).
4. Set Role to `Billing Account Administrator`.
5. Click Save.

## Step 4: Enable Cloud Billing API.
1. On Cloud console, navigate to Cloud Billing API using the search bar.
2. Click Enable.

That's all! Now once your cost amount exceeds budget amount (amount set in Step 1, which should be slightly below the credit amount to account for potential latency), billing will be stopped and you would have to re-enable it manually to continue using your API keys.

Learn more [here](https://cloud.google.com/billing/docs/how-to/notify#cap_disable_billing_to_stop_usage).