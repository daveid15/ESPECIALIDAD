function clonarSelect() {
    // Obtener el select original
    var selectOriginal = document.getElementById('selectOriginal');
    
    // Clonar el select
    var selectClonado = selectOriginal.cloneNode(true);
    
    // Cambiar el id del clon para evitar duplicaciones
    selectClonado.id = 'selectClonado';
    
    // Agregar el clon al contenedor
    var contenedorClon = document.getElementById('contenedorClon');
    contenedorClon.appendChild(selectClonado);
  }