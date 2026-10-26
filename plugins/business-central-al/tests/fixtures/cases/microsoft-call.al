codeunit 50010 "CRD Sales"
{
    var
        SalesPost: Codeunit "Sales-Post";
    procedure PostOrder()
    begin
        SalesPost.Run();
    end;
}
