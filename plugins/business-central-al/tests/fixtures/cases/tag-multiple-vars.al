codeunit 50010 "CRD Release"
{
    var
        FirstMgt, SecondMgt: Codeunit "TAG Work Order Mgt.";
    procedure ReleaseOrder()
    begin
        FirstMgt.Release();
        SecondMgt.Release();
    end;
}
