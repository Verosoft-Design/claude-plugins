codeunit 50010 "CRD First"
{
    var
        WorkOrderMgt: Codeunit "Sales-Post";

    procedure HasLocalTag()
    var
        WorkOrderMgt: Codeunit "TAG Work Order Mgt.";
    begin
        // Declaration alone is allowed.
    end;

    procedure CallsMicrosoft()
    begin
        WorkOrderMgt.Run();
    end;
}
codeunit 50011 "CRD Second"
{
    var
        WorkOrderMgt: Codeunit "Sales-Post";

    procedure CallsMicrosoft()
    begin
        WorkOrderMgt.Run();
    end;
}
