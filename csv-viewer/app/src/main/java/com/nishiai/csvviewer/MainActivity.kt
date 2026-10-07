package com.nishiai.csvviewer

import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/** Simple CSV parse: handles quoted fields with embedded commas and doubled quotes. */
fun parseCsv(text: String): List<List<String>> {
    val rows = mutableListOf<List<String>>()
    var field = StringBuilder()
    var row = mutableListOf<String>()
    var inQuotes = false
    var i = 0
    val s = text.replace("\r\n", "\n").replace("\r", "\n")
    while (i < s.length) {
        val c = s[i]
        when {
            inQuotes && c == '"' && i + 1 < s.length && s[i + 1] == '"' -> { field.append('"'); i++ }
            c == '"' -> inQuotes = !inQuotes
            !inQuotes && c == ',' -> { row.add(field.toString()); field = StringBuilder() }
            !inQuotes && c == '\n' -> { row.add(field.toString()); rows.add(row); field = StringBuilder(); row = mutableListOf() }
            else -> field.append(c)
        }
        i++
    }
    if (field.isNotEmpty() || row.isNotEmpty()) { row.add(field.toString()); rows.add(row) }
    return rows
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { CsvViewerApp(initialUri = intent?.data) }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CsvViewerApp(initialUri: Uri?) {
    var rows by remember { mutableStateOf<List<List<String>>>(emptyList()) }
    var fileName by remember { mutableStateOf<String?>(null) }
    var error by remember { mutableStateOf<String?>(null) }
    var query by remember { mutableStateOf("") }
    val scope = rememberCoroutineScope()

    val loadContent: (String, String?) -> Unit = { text, name ->
        rows = parseCsv(text)
        fileName = name
        error = null
    }

    val context = androidx.compose.ui.platform.LocalContext.current
    val openFile = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri: Uri? ->
        if (uri != null) {
            scope.launch {
                try {
                    val text = withContext(Dispatchers.IO) {
                        context.contentResolver.openInputStream(uri)?.bufferedReader()?.use { it.readText() } ?: ""
                    }
                    loadContent(text, uri.lastPathSegment)
                } catch (e: Exception) {
                    error = e.message
                }
            }
        }
    }

    // VIEW intent (deschis din alt app) se încarcă o singură dată
    LaunchedEffect(initialUri) {
        if (initialUri != null && rows.isEmpty()) {
            try {
                val text = withContext(Dispatchers.IO) {
                    context.contentResolver.openInputStream(initialUri)?.bufferedReader()?.use { it.readText() } ?: ""
                }
                loadContent(text, initialUri.lastPathSegment)
            } catch (e: Exception) {
                error = e.message
            }
        }
    }

    val sample = "Produs,Cantitate,Pret\nCiment 40kg,12,1440.00\nBetoniera,1,2899.00\nFire lustruite,40,2120.00"

    Scaffold(topBar = { TopAppBar(title = { Text("CSV Viewer — NISHIAI") }) }) { pad ->
        Column(Modifier.padding(pad).padding(12.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = { openFile.launch(arrayOf("text/csv", "text/comma-separated-values", "text/*")) }) { Text("Deschide CSV") }
                OutlinedButton(onClick = { loadContent(sample, "demo.csv") }) { Text("Exemplu") }
            }
            OutlinedTextField(
                value = query, onValueChange = { query = it },
                label = { Text("Caută (filtrează rândurile)") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )
            error?.let { Text("Eroare: $it", color = MaterialTheme.colorScheme.error) }
            if (rows.isEmpty()) {
                Text(if (fileName == null) "Deschide un fișier CSV sau apasă „Exemplu”." else "Fișier gol.")
            } else {
                val header = rows.first()
                val filtered = rows.drop(1).filter { r ->
                    query.isBlank() || r.any { it.contains(query, ignoreCase = true) }
                }
                Text("${header.size} coloane · ${filtered.size} rânduri${if (fileName != null) " · $fileName" else ""}",
                     style = MaterialTheme.typography.labelMedium)
                LazyColumn(Modifier.fillMaxSize()) {
                    items(filtered) { r ->
                        Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()).padding(vertical = 4.dp)) {
                            r.forEach { cell -> Text(cell, fontSize = 14.sp, modifier = Modifier.widthIn(min = 90.dp).padding(end = 12.dp)) }
                        }
                        HorizontalDivider()
                    }
                }
            }
        }
    }
}
