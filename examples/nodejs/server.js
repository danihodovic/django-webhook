// See example at https://webhooks.fyi/security/hmac
//
const express = require("express");
const crypto = require("crypto");
const morgan = require("morgan");

const app = express();
const port = 8001;
// Shared between the Express server and Django
const webhookSecret = "very-secret-token";

app.use(
  express.json({
    verify: (req, res, buf) => {
      req.rawBody = buf;
    },
  })
);
app.use(morgan("tiny"));

app.post("/webhook", (req, res) => {
  const timestamp = req.get("django-webhook-request-timestamp");
  const signaturesStr = req.get("django-webhook-signature-v1") || "";

  // Check if any of the provided signatures are valid
  for (const signature of signaturesStr.split(",")) {
    const hmac = crypto.createHmac("sha256", webhookSecret);
    hmac.update(timestamp + ":" + req.rawBody);
    const digest = Buffer.from(hmac.digest("hex"), "utf8");

    if (!crypto.timingSafeEqual(Buffer.from(signature, "utf8"), digest)) {
      console.log("Signature comparison failed.");
      res.statusCode = 400;
      res.send("Invalid signature");
      return;
    }
  }

  console.log("Successfully processed webhook");
  console.log(req.body);
  res.send("Success");
});

app.listen(port, "0.0.0.0", () => {
  console.log(`Example app listening on port ${port}`);
});
