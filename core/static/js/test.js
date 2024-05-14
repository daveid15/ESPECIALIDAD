function test(){
    const div_principal = document.createElement("div");
    select_insumo = document.createElement("select");
    select_insumo.name = "proveedor_insumo[]";
    select_insumo.id = "proveedor_insumo[]";

    option1 = document.createElement("option");
    option1.setAttribute("value", "1");
    option1Texto = document.createTextNode("Palta");
    option1.appendChild(option1Texto);
 
    option2 = document.createElement("option");
    option2.setAttribute("value", "2");
    option2Texto = document.createTextNode("Tomate");
    option2.appendChild(option2Texto);
 
    option3 = document.createElement("option");
    option3.setAttribute("value", "3");
    option3Texto = document.createTextNode("Pan");
    option3.appendChild(option3Texto);
 
    select_insumo.appendChild(option1);
    select_insumo.appendChild(option2);
    select_insumo.appendChild(option3);
    document.body.appendChild(select_insumo);
    
};