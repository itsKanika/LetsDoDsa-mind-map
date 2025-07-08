const CompartmentButton = ({ label, onClick }) => (
  <button
    onClick={onClick}
    className="flex flex-col items-center justify-center h-50 border rounded-md px-3 py-2 hover:bg-slate-100 transition"
  >
   
    <span className="text-xs">{label.toUpperCase()}</span>
  </button>
);

export default CompartmentButton;