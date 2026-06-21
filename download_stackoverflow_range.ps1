param(
    [Parameter(Mandatory = $true)]
    [string]$StartDate,

    [Parameter(Mandatory = $true)]
    [string]$EndDate,

    [string]$OutputRoot = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $OutputRoot = Join-Path $PSScriptRoot "data\stackoverflow_2025"
}

$rangeToken = "{0}_to_{1}" -f $StartDate.Replace("-", ""), $EndDate.Replace("-", "")
$outputDir = Join-Path $OutputRoot $rangeToken
$questionsFile = Join-Path $outputDir "questions.jsonl"
$answersFile = Join-Path $outputDir "answers.jsonl"
$mergedFile = Join-Path $outputDir "qa_merged.jsonl"

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

if (Test-Path $questionsFile) { Remove-Item -LiteralPath $questionsFile -Force }
if (Test-Path $answersFile) { Remove-Item -LiteralPath $answersFile -Force }
if (Test-Path $mergedFile) { Remove-Item -LiteralPath $mergedFile -Force }

$pageSize = 100
$site = "stackoverflow"
$baseUrl = "https://api.stackexchange.com/2.3"

function Invoke-StackApi {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Url
    )

    Start-Sleep -Milliseconds 250
    $response = Invoke-RestMethod -Uri $Url -Method Get -Headers @{ "Accept-Encoding" = "gzip" }

    if ($null -ne $response.backoff) {
        Start-Sleep -Seconds ([int]$response.backoff)
    }

    return $response
}

function Get-UnixTime {
    param(
        [Parameter(Mandatory = $true)]
        [datetime]$Date
    )

    return [int][DateTimeOffset]::new($Date.ToUniversalTime()).ToUnixTimeSeconds()
}

$start = [datetime]::ParseExact($StartDate, "yyyy-MM-dd", $null)
$end = [datetime]::ParseExact($EndDate, "yyyy-MM-dd", $null)

if ($end -lt $start) {
    throw "EndDate must be greater than or equal to StartDate."
}

$fromDate = Get-UnixTime -Date $start
$toDate = Get-UnixTime -Date ($end.Date.AddDays(1).AddSeconds(-1))

Write-Host ("Starting range download: {0} to {1}" -f $StartDate, $EndDate)

$questionList = New-Object System.Collections.Generic.List[object]
$questionMap = @{}
$page = 1

do {
    $url = "$baseUrl/questions?page=$page&pagesize=$pageSize&fromdate=$fromDate&todate=$toDate&order=asc&sort=creation&site=$site&filter=withbody"
    $response = Invoke-StackApi -Url $url

    foreach ($item in $response.items) {
        $qid = [string]$item.question_id
        if (-not $questionMap.ContainsKey($qid)) {
            $questionMap[$qid] = $item
            $questionList.Add($item)
            ($item | ConvertTo-Json -Depth 20 -Compress) | Add-Content -LiteralPath $questionsFile -Encoding utf8
        }
    }

    Write-Host ("Question page {0} done, page items {1}, unique total {2}" -f $page, $response.items.Count, $questionList.Count)
    $page++

    if ($page -gt 25 -and $response.has_more) {
        throw "This date range exceeds the 25-page unauthenticated API limit. Use a smaller range."
    }
} while ($response.has_more)

Write-Host ("Question download complete, total {0}" -f $questionList.Count)

$questionIds = $questionList | ForEach-Object { $_.question_id } | Where-Object { $null -ne $_ }
$answerMap = @{}

Write-Host "Starting answer download..."

for ($i = 0; $i -lt $questionIds.Count; $i += 100) {
    $upperIndex = [Math]::Min($i + 99, $questionIds.Count - 1)
    if ($i -eq $upperIndex) {
        $chunk = @($questionIds[$i])
    } else {
        $chunk = @($questionIds[$i..$upperIndex])
    }

    $ids = ($chunk -join ";")
    $page = 1

    do {
        $url = "$baseUrl/questions/$ids/answers?page=$page&pagesize=$pageSize&order=desc&sort=votes&site=$site&filter=withbody"
        $response = Invoke-StackApi -Url $url

        foreach ($answer in $response.items) {
            $key = [string]$answer.question_id
            if (-not $answerMap.ContainsKey($key)) {
                $answerMap[$key] = New-Object System.Collections.Generic.List[object]
            }

            $answerMap[$key].Add($answer)
            ($answer | ConvertTo-Json -Depth 20 -Compress) | Add-Content -LiteralPath $answersFile -Encoding utf8
        }

        Write-Host ("Answer chunk {0}-{1}, page {2} done, page items {3}" -f ($i + 1), ($upperIndex + 1), $page, $response.items.Count)
        $page++
    } while ($response.has_more)
}

Write-Host ("Answer download complete, covered questions {0}" -f $answerMap.Keys.Count)

Write-Host "Building merged RAG dataset file..."

foreach ($question in $questionList) {
    $qid = [string]$question.question_id
    $answerItems = @()

    if ($answerMap.ContainsKey($qid)) {
        $answerItems = @($answerMap[$qid].ToArray())
    }

    $record = [PSCustomObject]@{
        question_id = $question.question_id
        title = $question.title
        question_body = $question.body
        tags = $question.tags
        creation_date = $question.creation_date
        score = $question.score
        view_count = $question.view_count
        answer_count = $question.answer_count
        accepted_answer_id = $question.accepted_answer_id
        link = $question.link
        answers = $answerItems
    }

    ($record | ConvertTo-Json -Depth 30 -Compress) | Add-Content -LiteralPath $mergedFile -Encoding utf8
}

Write-Host "All done. Output files:"
Write-Host $questionsFile
Write-Host $answersFile
Write-Host $mergedFile
