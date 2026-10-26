// codeunit 999999 "Bad" { WorkOrderMgt.Release(); }
/* tableextension 999999 "Bad" extends Customer {
   fields { field(999999; Bad; Boolean) { } }
} */
codeunit 50010 "CRD Escaped ""Name"""
{
    var
        WorkOrderMgt: Codeunit "TAG Work Order Mgt.";
        FakeSourceLbl: Label 'It''s codeunit 999999 "Bad" { WorkOrderMgt.Release(); }';
    procedure IgnoreText()
    begin
        Message('/* not a comment */ WorkOrderMgt.Release(); // neither is this');
        // WorkOrderMgt.Release();
        /* WorkOrderMgt.Release(); Codeunit.Run(Codeunit::"TAG Work Order Mgt."); */
    end;
}
