function test(){
    const div_principal = document.createElement("div");
    const div_insumo = document.createElement("div");
    const span = document.createElement("span");
    span.innerHTML = "proveedor_insumo";
    select_insumo = document.createElement("select");
    select_insumo.name = "proveedor_insumo";
    select_insumo.id = "proveedor_insumo";


    option1 = document.createElement("option");
    option1.setAttribute("value", "Palta");
    option1Texto = document.createTextNode("Palta");
    option1.appendChild(option1Texto);
 
    option2 = document.createElement("option");
    option2.setAttribute("value", "Tomate");
    option2Texto = document.createTextNode("Tomate");
    option2.appendChild(option2Texto);
 
    option3 = document.createElement("option");
    option3.setAttribute("value", "Pan");
    option3Texto = document.createTextNode("Pan");
    option3.appendChild(option3Texto);
 
    select_insumo.appendChild(option1);
    select_insumo.appendChild(option2);
    select_insumo.appendChild(option3);
    document.getElementById("container").appendChild(select_insumo);

    
};