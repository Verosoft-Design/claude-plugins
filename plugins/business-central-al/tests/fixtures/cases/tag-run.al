codeunit 50010 "CRD Run"
{
    procedure RunOrder()
    begin
        Codeunit.Run(Codeunit::"TAG Work Order Mgt.");
        Codeunit.Run(70015000);
    end;
}
