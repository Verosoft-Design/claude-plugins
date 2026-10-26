codeunit 50010 "CRD Release"
{
    var
        WorkOrderMgt: Codeunit "TAG Work Order Mgt.";

    procedure ReleaseOrder()
    begin
        // The call must be listed by the TAG team.
        WorkOrderMgt.Release();
    end;
}
