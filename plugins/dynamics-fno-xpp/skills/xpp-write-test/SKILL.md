---
name: xpp-write-test
description: Write an X++ SysTest test class (SysTestCase) for Dynamics 365 Finance and Operations, red first, with test data from the Acceptance Test Library (ATL) for standard tables and plain buffers for your own. Use when asked to write, scaffold or generate X++ tests, to pin a bug with a failing test, or for the red step of TDD.
argument-hint: "[class or table under test] [behaviour]"
---

# Write an X++ test

The rules here are the short form. The MCP holds the long form, taken from the shipped code base (784 test classes, 1,105 ATL data classes, read on a VM on 2026-09-02). Read it before the first test in a session: `get_knowledge` with kind `knowledge` and topics `["unit-testing", "systest-attributes", "test-data-atl"]`.

## Decide first

- **Which framework.** A rule such as validation, a calculation or defaulting gets a SysTestCase unit test. A business process (create an order, post it, check the journal) also uses SysTestCase, with its arrange step from ATL.
- **Where it lives.** A test class must be in the model under test, or in a test model that references it. A separate test package is cleaner, but it's a new package and a repo decision: ask before creating one. ATL needs `ATLApplicationSuite` (and `AtlFoundation`; `AtlPersonnel` for HR) in the model's Descriptor `ModuleReferences`. Adding them changes the Descriptor, so ask first too.
- **What it pins.** One behaviour per method, named for it: `testDueDateDefaultsFromLeadTime`, not `testInit`.

## Shape (as shipped tests use it)

```xpp
[
SysTestTarget(classStr(TAGWorkOrderDefaults), UtilElementType::Class),
SysTestGranularity(SysTestGranularity::Unit)
]
class TAGWorkOrderDefaultsTest extends SysTestCase
{
    public void setUp()
    {
        super();
        // shared arrange; every test method runs in its own transaction, rolled back afterwards
    }

    [SysTestMethod]
    public void testDueDateDefaultsFromLeadTime()
    {
        // Arrange
        TAGControls controls = TAGControls::find();   // own table: plain buffer + initValue()/insert()
        // Act
        // Assert: a value, a count or a RecId (assertNotNull on a buffer only says a select found a row)
        this.assertEquals(expected, actual, 'due date = today + lead time');
    }
}
```

- The class extends `SysTestCase`, which gives you the asserts: `assertEquals`, `assertNotEqual`, `assertTrue`, `assertFalse`, `assertRealEquals`, `assertUTCDateTimeEquals`, `fail`, …
- Methods are `public void`, carry `[SysTestMethod]` and are named `test…`. Several attributes on one method share **one** bracket: `[SysTestMethod, SysTestCheckInTest]`. Two bracket lines is a parse error.
- **Expected exceptions are declared before the call:** `this.parmExceptionExpected(true, 'message');`. There is no `assertExpectedException`.
- **Isolation:** each method's writes are rolled back. Don't use the obsolete `SysTestSuiteCompanyIsolate*` suites; use `[SysTestCaseDataDependency('usmf')]` or `changecompany` when a company matters. `[SysTestCaseAutomaticNumberSequences]` when the code draws numbers.
- **ATL arrange:** `AtlDataRootNode data = AtlDataRootNode::construct();` then `CustTable customer = data.cust().customers().default().record();`. Forgetting `.record()` is a type error. `default()` reuses demo data, `createDefault()` makes a new record, and transactions only have `createDefault()`. ATL doesn't cover your own tables.
- **No mocking framework:** isolate dependencies behind a small class or interface you can swap.

## Red first, then green

1. Scaffold: MCP `generate_object` (mode `pattern`, pattern `systest`, name the target class) emits one method per target method, each ending in `this.fail(...)`. Or write the class by hand from the shape above. Register it in the `.rnrproj`; `d365fo_file` create does it.
2. Write the assertion for the behaviour. Build (`xpp-build`): red must be a **failing assertion**, not a broken file.
3. Run it (`xpp-run-tests`) and see it fail for the right reason. A test that passes on its first run has proven nothing.
4. Implement, build, run again: green. Then run the model's other test classes.

Without a VM run, say so: "test written and lint-clean; not compiled; not run".

Evidence to quote: the class and method names, the red run's failure message, the green run's totals.
