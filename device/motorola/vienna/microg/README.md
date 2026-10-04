# microG

Bundles the official microG release APKs as privileged product apps. crDroid's
package manager (`ComputerEngine.isMicrogSigned`) already spoofs the Google
signature, but only for `com.google.android.gms` and `com.android.vending` with
microG's `fake-signature` metadata.

The APKs are git-ignored. To fetch or update them, read `index-v1.json` from
`https://microg.org/fdroid/repo/index-v1.jar`, download the newest APK for each
package, and check its SHA-256 against the index. Also confirm that the signer
certificate SHA-256 is
`9bd06727e62796c0130eb6dab39b73157451582cbd138e86c468acc395d14165`:

| File | Package | Version | SHA-256 |
| --- | --- | --- | --- |
| `GmsCore.apk` | `com.google.android.gms` | 0.3.17.252432 (252432034) | `e5e6cba078bdec812b5450599350e5c1a12c8b7438da5bf77123af170f8c1a35` |
| `FakeStore.apk` | `com.android.vending` | 0.3.17.40226 (84022634) | `9b8616011cc8f026bcbbe094df850794abb9d6d9f23214d7a8f8c4d1033ea012` |

When updating, regenerate `privapp-permissions-microg.xml` from the privileged
permissions the new APKs request. A missing entry stops the device from booting.
