function pid = get_process_id()
import System.Diagnostics.*
process = System.Diagnostics.Process.GetCurrentProcess();
pid = process.Id;
end
