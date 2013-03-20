Recommended Roll Process
========================

Step 1: Use release-tool to prepare your branch
-----------------------------------------------

	developer$ release-tool roll qa to prod
	---> pavement.roll
	---> pavement.load_releaserc
	Special permission is required to roll to this branch.
	Password: 

	You need a passphrase to unlock the secret key for
	user: "Aaron Spaulding <aaron@sachimp.com>"
	2048-bit RSA key, ID 05A268FC, created 2013-01-06

	Rolled qa to prod.

Step 2: Push the branch and tag
-------------------------------

	developer$ git push origin prod
	developer$ git tag
	roll-from-qa-to-prod-2013-01-06T12.53.36.927721
	roll-from-qa-to-prod-2013-01-06T12.58.34.295814
	developer$ git push origin roll-from-qa-to-prod-2013-01-06T12.58.34.295814

Step 2: Fetch the tag
---------------------

	server$ git fetch origin roll-from-qa-to-prod-2013-01-06T12.58.34.295814

Step 3: Verify it
-----------------

	server$ git tag --verify roll-from-qa-to-prod-2013-01-06T12.58.34.295814
	object 53c66e0df04ae66223e56885dfee1ddd01924e9f
	type commit
	tag roll-from-qa-to-prod-2013-01-06T12.58.34.295814
	tagger Aaron Spaulding <aaron@sachimp.com> 1357477114 -0500

	Roll from qa to prod with special permission by Aaron Spaulding <aaron@sachimp.com>.

	*****
	This was an automated tag created by Release Tool
	gpg: Signature made Sun Jan  6 07:58:34 2013 EST using RSA key ID 05A268FC
	gpg: Good signature from "Aaron Spaulding <aaron@sachimp.com>"

Step 4: If its valid, checkout
------------------------------

You're all set.

	server$ git checkout roll-from-qa-to-prod-2013-01-06T12.58.34.295814

Step 4.5: If its not valid, worry
---------------------------------

Because Release Tool automatically signs all rolls that require special
permission, you can be sure someone tampered with the commit.

	developer$ git diff prod..origin/prod

