tableextension 50010 "CRD Work Order" extends "TAG Work Order"
{
    fields { field(50011; "CRD Instructions"; Text[100]) { } }
}
pageextension 50012 "CRD Work Order Page" extends "TAG Work Order"
{
    layout { addlast(Content) { field(CRDInstructions; Rec."CRD Instructions") { } } }
}
codeunit 50013 "CRD Subscriber"
{
    [EventSubscriber(ObjectType::Codeunit, Codeunit::"TAG Work Order Mgt.", 'OnAfterRelease', '', false, false)]
    local procedure AfterRelease()
    var
        WorkOrdersApi: Page "TAG API Work Orders";
    begin
        WorkOrdersApi.Run();
    end;
}
