codeunit 50010 "CRD Release"
{
    procedure ReleaseOrder()
    var
        WorkOrderMgt: Codeunit 70015000;
    begin
        WorkOrderMgt.Release();
    end;
}
