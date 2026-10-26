codeunit 50010 "CRD Release"
{
    procedure ReleaseOrder()
    begin
        WorkOrderMgt.Release();
    end;

    procedure OtherWork()
    begin
        case true of
            true: begin end;
        end;
    end;

    var
        WorkOrderMgt: Codeunit "TAG Work Order Mgt.";
}
