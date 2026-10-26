table 50000 "CRD Settings"
{
    fields
    {
        field(50000; "CRD Enabled"; Boolean) { }
        field(50199; "CRD Description"; Text[100]) { }
    }
}
tableextension 50001 "CRD Customer" extends Customer
{
    fields { field(50002; "CRD Instructions"; Text[100]) { } }
}
enumextension 50003 "CRD Status" extends "Sales Document Status"
{
    value(50004; "CRD Ready") { }
}
page 50005 "CRD Settings Page"
{
    SourceTable = "CRD Settings";
    layout { area(Content) { field(Enabled; Rec."CRD Enabled") { } } }
}
