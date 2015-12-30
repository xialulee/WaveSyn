function pid = processId()
import System.Diagnostics.*
process = System.Diagnostics.Process.GetCurrentProcess();
pid = process.Id;
end