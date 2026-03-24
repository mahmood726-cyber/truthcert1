/**
 * Validate command - Validate input data format
 */

import chalk from 'chalk';
import { loadData } from '../utils/data-loader';

interface ValidateOptions {
  strict?: boolean;
}

export async function validateCommand(file: string, options: ValidateOptions): Promise<void> {
  console.log(chalk.cyan(`\nValidating: ${file}`));
  console.log('─'.repeat(50));

  const errors: string[] = [];
  const warnings: string[] = [];
  let data: any[];

  try {
    data = await loadData(file);
  } catch (error) {
    console.log(chalk.red('✗ Failed to load file'));
    console.error(chalk.red(`  ${(error as Error).message}`));
    process.exit(1);
  }

  console.log(chalk.green(`✓ File loaded successfully`));
  console.log(`  Records found: ${data.length}`);

  if (data.length === 0) {
    errors.push('No data records found in file');
  }

  // Check data format
  if (data.length > 0) {
    const firstRow = data[0];
    const hasEffectSize = 'yi' in firstRow && 'vi' in firstRow;
    const hasBinary =
      ('events1' in firstRow && 'total1' in firstRow && 'events2' in firstRow && 'total2' in firstRow) ||
      ('ai' in firstRow && 'bi' in firstRow && 'ci' in firstRow && 'di' in firstRow);
    const hasContinuous =
      ('mean1' in firstRow && 'sd1' in firstRow && 'n1' in firstRow && 'mean2' in firstRow && 'sd2' in firstRow && 'n2' in firstRow) ||
      ('m1i' in firstRow && 'sd1i' in firstRow && 'n1i' in firstRow && 'm2i' in firstRow && 'sd2i' in firstRow && 'n2i' in firstRow);

    if (hasEffectSize) {
      console.log(chalk.green('✓ Detected format: Pre-calculated effect sizes'));
      validateEffectSizeData(data, errors, warnings, options.strict);
    } else if (hasBinary) {
      console.log(chalk.green('✓ Detected format: Binary outcome data'));
      validateBinaryData(data, errors, warnings, options.strict);
    } else if (hasContinuous) {
      console.log(chalk.green('✓ Detected format: Continuous outcome data'));
      validateContinuousData(data, errors, warnings, options.strict);
    } else {
      errors.push('Unable to detect data format. Expected effect sizes (yi, vi), binary (events1, total1, events2, total2), or continuous (mean1, sd1, n1, mean2, sd2, n2)');
    }
  }

  // Report results
  console.log('\n' + '─'.repeat(50));

  if (errors.length === 0 && warnings.length === 0) {
    console.log(chalk.green.bold('✓ Validation passed - No issues found'));
    process.exit(0);
  }

  if (warnings.length > 0) {
    console.log(chalk.yellow(`\n⚠ ${warnings.length} Warning(s):`));
    warnings.forEach((w, i) => console.log(chalk.yellow(`  ${i + 1}. ${w}`)));
  }

  if (errors.length > 0) {
    console.log(chalk.red(`\n✗ ${errors.length} Error(s):`));
    errors.forEach((e, i) => console.log(chalk.red(`  ${i + 1}. ${e}`)));
    process.exit(1);
  }

  process.exit(0);
}

function validateEffectSizeData(
  data: any[],
  errors: string[],
  warnings: string[],
  strict?: boolean
): void {
  data.forEach((row, i) => {
    const rowNum = i + 1;

    // Required fields
    if (typeof row.yi !== 'number' || isNaN(row.yi)) {
      errors.push(`Row ${rowNum}: Invalid or missing 'yi' (effect size)`);
    }

    if (typeof row.vi !== 'number' || isNaN(row.vi)) {
      errors.push(`Row ${rowNum}: Invalid or missing 'vi' (variance)`);
    } else if (row.vi <= 0) {
      errors.push(`Row ${rowNum}: Variance 'vi' must be positive (got ${row.vi})`);
    }

    // Optional but recommended
    if (strict && !row.study && !row.id) {
      warnings.push(`Row ${rowNum}: No study identifier provided`);
    }

    // Check for extreme values
    if (Math.abs(row.yi) > 10) {
      warnings.push(`Row ${rowNum}: Effect size may be extreme (yi = ${row.yi})`);
    }
  });
}

function validateBinaryData(
  data: any[],
  errors: string[],
  warnings: string[],
  strict?: boolean
): void {
  data.forEach((row, i) => {
    const rowNum = i + 1;

    const events1 = typeof row.events1 === 'number' ? row.events1 : row.ai;
    const total1 = typeof row.total1 === 'number'
      ? row.total1
      : (typeof row.ai === 'number' && typeof row.bi === 'number' ? row.ai + row.bi : undefined);
    const events2 = typeof row.events2 === 'number' ? row.events2 : row.ci;
    const total2 = typeof row.total2 === 'number'
      ? row.total2
      : (typeof row.ci === 'number' && typeof row.di === 'number' ? row.ci + row.di : undefined);

    const fields: Record<string, number | undefined> = { events1, total1, events2, total2 };
    Object.entries(fields).forEach(([field, value]) => {
      if (typeof value !== 'number' || isNaN(value)) {
        errors.push(`Row ${rowNum}: Invalid or missing '${field}'`);
      } else if (value < 0) {
        errors.push(`Row ${rowNum}: '${field}' cannot be negative`);
      } else if (!Number.isInteger(value)) {
        warnings.push(`Row ${rowNum}: '${field}' should be an integer`);
      }
    });

    if (typeof events1 !== 'number' || typeof total1 !== 'number' ||
        typeof events2 !== 'number' || typeof total2 !== 'number') {
      return;
    }

    // Logical checks
    if (events1 > total1) {
      errors.push(`Row ${rowNum}: events1 (${events1}) cannot exceed total1 (${total1})`);
    }
    if (events2 > total2) {
      errors.push(`Row ${rowNum}: events2 (${events2}) cannot exceed total2 (${total2})`);
    }

    // Zero cell check
    if (events1 === 0 || events2 === 0 ||
        events1 === total1 || events2 === total2) {
      warnings.push(`Row ${rowNum}: Contains zero cells (continuity correction will be applied)`);
    }

    // Sample size warnings
    if (strict && (total1 < 10 || total2 < 10)) {
      warnings.push(`Row ${rowNum}: Very small sample size`);
    }
  });
}

function validateContinuousData(
  data: any[],
  errors: string[],
  warnings: string[],
  strict?: boolean
): void {
  data.forEach((row, i) => {
    const rowNum = i + 1;

    const mean1 = typeof row.mean1 === 'number' ? row.mean1 : row.m1i;
    const sd1 = typeof row.sd1 === 'number' ? row.sd1 : row.sd1i;
    const n1 = typeof row.n1 === 'number' ? row.n1 : row.n1i;
    const mean2 = typeof row.mean2 === 'number' ? row.mean2 : row.m2i;
    const sd2 = typeof row.sd2 === 'number' ? row.sd2 : row.sd2i;
    const n2 = typeof row.n2 === 'number' ? row.n2 : row.n2i;

    const fields: Record<string, number | undefined> = { mean1, sd1, n1, mean2, sd2, n2 };
    Object.entries(fields).forEach(([field, value]) => {
      if (typeof value !== 'number' || isNaN(value)) {
        errors.push(`Row ${rowNum}: Invalid or missing '${field}'`);
      }
    });

    if (typeof sd1 !== 'number' || typeof sd2 !== 'number' ||
        typeof n1 !== 'number' || typeof n2 !== 'number') {
      return;
    }

    // SD must be positive
    if (sd1 <= 0) {
      errors.push(`Row ${rowNum}: sd1 must be positive (got ${sd1})`);
    }
    if (sd2 <= 0) {
      errors.push(`Row ${rowNum}: sd2 must be positive (got ${sd2})`);
    }

    // N must be positive integer
    if (n1 <= 0 || !Number.isInteger(n1)) {
      errors.push(`Row ${rowNum}: n1 must be a positive integer (got ${n1})`);
    }
    if (n2 <= 0 || !Number.isInteger(n2)) {
      errors.push(`Row ${rowNum}: n2 must be a positive integer (got ${n2})`);
    }

    // Sample size warnings
    if (strict && (n1 < 10 || n2 < 10)) {
      warnings.push(`Row ${rowNum}: Very small sample size`);
    }
  });
}
