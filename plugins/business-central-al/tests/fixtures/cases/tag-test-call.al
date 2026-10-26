codeunit 50210 "CRD Release Tests"
{
    var
        WorkOrderMgt: Codeunit "TAG Work Order Mgt.";
    [Test]
    procedure ReleaseOrder()
    begin
        WorkOrderMgt.Release();
    end;
}
